"""
Source Normalization Engine for NETRA Phase 5.
Translates heterogeneous raw synthetic sensor payloads into standardized
CanonicalObservation instances with complete audit lineage (NormalizationTrace).
"""

from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List, Optional, Tuple
import logging

from models.common import Coordinates
from models.fusion_intelligence import (
    CanonicalObservation,
    NormalizationTraceItem,
    Velocity,
)

logger = logging.getLogger("netra.fusion.normalization")


class SourceNormalizer:
    """
    Normalizes multi-sensor payloads into canonical observation models.
    Supports field alias mapping, unit conversions, and generates immutable
    transformation audit traces without fabricating unobserved fields.
    """

    LATITUDE_ALIASES = ["latitude", "lat", "lat_deg", "y", "geo_lat"]
    LONGITUDE_ALIASES = ["longitude", "lon", "lng", "lon_deg", "x", "geo_lon"]
    ALTITUDE_ALIASES = ["altitude_m", "altitude", "alt", "alt_m", "elevation"]
    
    SPEED_ALIASES = ["speed", "velocity", "speed_kmh", "spd", "vel", "ground_speed"]
    SPEED_MPS_ALIASES = ["speed_mps", "velocity_mps", "vel_mps"]
    SPEED_KNOTS_ALIASES = ["speed_knots", "speed_kts", "knots"]

    HEADING_ALIASES = ["heading_deg", "heading", "course", "bearing", "bearing_deg", "track_heading"]
    ENTITY_HINT_ALIASES = ["entity_hint", "track_id", "object_id", "target_id", "entity_id", "id", "callsign"]
    EVENT_TYPE_ALIASES = ["event_type", "type", "classification", "category", "event", "action"]
    TIMESTAMP_ALIASES = ["timestamp", "time", "datetime", "ts", "time_iso", "observed_at"]
    SECTOR_ALIASES = ["sector_id", "sector", "zone", "area"]

    @classmethod
    def normalize_observation(
        cls,
        raw_obs: Dict[str, Any],
        default_source_id: str = "SYNTH_FEED",
        default_source_type: str = "TELEMETRY",
    ) -> CanonicalObservation:
        """
        Transforms a raw observation payload into a CanonicalObservation,
        recording every mapped key and unit transformation in normalization_trace.
        """
        trace: List[NormalizationTraceItem] = []
        attrs = dict(raw_obs.get("attributes", {})) if isinstance(raw_obs.get("attributes"), dict) else {}

        # 1. Source Identification
        source_id = str(raw_obs.get("source_id") or raw_obs.get("sensor_id") or default_source_id)
        source_type = str(raw_obs.get("source_type") or raw_obs.get("sensor_type") or default_source_type)

        # 2. Timestamp Normalization
        timestamp, ts_orig_key, ts_orig_val, ts_conv = cls._extract_timestamp(raw_obs)
        if ts_orig_key:
            trace.append(NormalizationTraceItem(
                field="timestamp",
                original_field=ts_orig_key,
                original_value=ts_orig_val,
                normalized_value=timestamp.isoformat(),
                conversion=ts_conv,
            ))

        received_at = timestamp
        if "received_at" in raw_obs and isinstance(raw_obs["received_at"], datetime):
            received_at = raw_obs["received_at"]


        # 3. Entity Hint
        entity_hint = None
        for alias in cls.ENTITY_HINT_ALIASES:
            if alias in raw_obs and raw_obs[alias] is not None:
                entity_hint = str(raw_obs[alias])
                trace.append(NormalizationTraceItem(
                    field="entity_hint",
                    original_field=alias,
                    original_value=raw_obs[alias],
                    normalized_value=entity_hint,
                    conversion="alias_map",
                ))
                break

        # 4. Position & Coordinates
        position, pos_traces = cls._extract_position(raw_obs)
        trace.extend(pos_traces)

        # 5. Velocity & Kinematics
        velocity, vel_traces = cls._extract_velocity(raw_obs)
        trace.extend(vel_traces)

        # 6. Event Type
        event_type = None
        for alias in cls.EVENT_TYPE_ALIASES:
            if alias in raw_obs and raw_obs[alias] is not None:
                event_type = str(raw_obs[alias]).upper()
                trace.append(NormalizationTraceItem(
                    field="event_type",
                    original_field=alias,
                    original_value=raw_obs[alias],
                    normalized_value=event_type,
                    conversion="uppercase_canonical",
                ))
                break

        # 7. Uncertainty & Quality
        uncertainty = float(raw_obs.get("position_uncertainty_km", raw_obs.get("uncertainty_km", raw_obs.get("accuracy_km", 0.10))))
        quality = float(raw_obs.get("quality", raw_obs.get("confidence", 1.0)))
        quality = max(0.0, min(1.0, quality))

        # 8. Deterministic Observation ID
        obs_id = raw_obs.get("observation_id") or raw_obs.get("obs_id")
        if not obs_id:
            # Deterministic hash of source + timestamp + coordinates or entity hint
            sig = f"{source_id}_{timestamp.isoformat()}_{entity_hint}_{position.latitude if position else 0}_{position.longitude if position else 0}"
            obs_id = f"OBS-{hashlib.sha256(sig.encode('utf-8')).hexdigest()[:10].upper()}"

        # Preserve unmapped extra fields into attributes
        for k, v in raw_obs.items():
            if k not in (
                "observation_id", "obs_id", "source_id", "source_type", "timestamp", "received_at",
                "position", "coordinates", "location", "velocity", "attributes", "quality", "provenance"
            ):
                if k not in attrs:
                    attrs[k] = v

        return CanonicalObservation(
            observation_id=obs_id,
            source_id=source_id,
            source_type=source_type,
            timestamp=timestamp,
            received_at=received_at,
            entity_hint=entity_hint,
            position=position,
            position_uncertainty_km=uncertainty,
            velocity=velocity,
            event_type=event_type,
            attributes=attrs,
            quality=quality,
            provenance={
                "ingested_by": "NETRA_PHASE_5_NORMALIZER",
                "raw_format": type(raw_obs).__name__,
                "source_id": source_id,
            },
            normalization_trace=trace,
            raw_data=raw_obs,
        )

    @classmethod
    def _extract_timestamp(cls, raw: Dict[str, Any]) -> Tuple[datetime, Optional[str], Any, Optional[str]]:
        for alias in cls.TIMESTAMP_ALIASES:
            if alias in raw and raw[alias] is not None:
                val = raw[alias]
                if isinstance(val, datetime):
                    if val.tzinfo is None:
                        val = val.replace(tzinfo=timezone.utc)
                    return val, alias, val, "tz_normalize_utc"
                if isinstance(val, (int, float)):
                    # Epoch timestamp
                    if val > 1e11:  # milliseconds
                        val = val / 1000.0
                    dt = datetime.fromtimestamp(val, tz=timezone.utc)
                    return dt, alias, raw[alias], "epoch_to_datetime_utc"
                if isinstance(val, str):
                    try:
                        clean_str = val.replace("Z", "+00:00")
                        dt = datetime.fromisoformat(clean_str)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        return dt, alias, val, "iso_string_to_datetime_utc"
                    except Exception:
                        pass
        # Fallback to current UTC if no timestamp specified
        now = datetime.now(timezone.utc)
        return now, None, None, "fallback_now_utc"

    @classmethod
    def _extract_position(cls, raw: Dict[str, Any]) -> Tuple[Optional[Coordinates], List[NormalizationTraceItem]]:
        traces: List[NormalizationTraceItem] = []
        lat, lon, alt, sector = None, None, None, None

        # Check nested location/position/coordinates dict
        container = raw
        for nested in ["position", "coordinates", "location"]:
            if nested in raw and isinstance(raw[nested], dict):
                container = raw[nested]
                break

        # Latitude
        for alias in cls.LATITUDE_ALIASES:
            if alias in container and container[alias] is not None:
                try:
                    lat = float(container[alias])
                    traces.append(NormalizationTraceItem(
                        field="position.latitude",
                        original_field=alias,
                        original_value=container[alias],
                        normalized_value=lat,
                        conversion="float_cast",
                    ))
                    break
                except (ValueError, TypeError):
                    pass

        # Longitude
        for alias in cls.LONGITUDE_ALIASES:
            if alias in container and container[alias] is not None:
                try:
                    lon = float(container[alias])
                    traces.append(NormalizationTraceItem(
                        field="position.longitude",
                        original_field=alias,
                        original_value=container[alias],
                        normalized_value=lon,
                        conversion="float_cast",
                    ))
                    break
                except (ValueError, TypeError):
                    pass

        # Altitude
        for alias in cls.ALTITUDE_ALIASES:
            if alias in container and container[alias] is not None:
                try:
                    alt = float(container[alias])
                    traces.append(NormalizationTraceItem(
                        field="position.altitude_m",
                        original_field=alias,
                        original_value=container[alias],
                        normalized_value=alt,
                        conversion="float_cast",
                    ))
                    break
                except (ValueError, TypeError):
                    pass

        # Sector
        for alias in cls.SECTOR_ALIASES:
            if alias in container and container[alias] is not None:
                sector = str(container[alias])
                traces.append(NormalizationTraceItem(
                    field="position.sector_id",
                    original_field=alias,
                    original_value=container[alias],
                    normalized_value=sector,
                    conversion="string_cast",
                ))
                break

        if lat is not None and lon is not None:
            # Validate bounds
            lat = max(-90.0, min(90.0, lat))
            lon = max(-180.0, min(180.0, lon))
            return Coordinates(latitude=lat, longitude=lon, altitude_m=alt, sector_id=sector), traces

        return None, traces

    @classmethod
    def _extract_velocity(cls, raw: Dict[str, Any]) -> Tuple[Optional[Velocity], List[NormalizationTraceItem]]:
        traces: List[NormalizationTraceItem] = []
        speed_kmh, heading = None, None

        container = raw
        for nested in ["velocity", "motion", "kinematics"]:
            if nested in raw and isinstance(raw[nested], dict):
                container = raw[nested]
                break

        # Check speed in km/h
        for alias in cls.SPEED_ALIASES:
            if alias in container and container[alias] is not None:
                try:
                    speed_kmh = float(container[alias])
                    traces.append(NormalizationTraceItem(
                        field="velocity.speed_kmh",
                        original_field=alias,
                        original_value=container[alias],
                        normalized_value=speed_kmh,
                        conversion="float_cast_kmh",
                    ))
                    break
                except (ValueError, TypeError):
                    pass

        # Check speed in m/s
        if speed_kmh is None:
            for alias in cls.SPEED_MPS_ALIASES:
                if alias in container and container[alias] is not None:
                    try:
                        mps = float(container[alias])
                        speed_kmh = round(mps * 3.6, 2)
                        traces.append(NormalizationTraceItem(
                            field="velocity.speed_kmh",
                            original_field=alias,
                            original_value=container[alias],
                            normalized_value=speed_kmh,
                            conversion="mps_to_kmh_x3.6",
                        ))
                        break
                    except (ValueError, TypeError):
                        pass

        # Check speed in knots
        if speed_kmh is None:
            for alias in cls.SPEED_KNOTS_ALIASES:
                if alias in container and container[alias] is not None:
                    try:
                        kts = float(container[alias])
                        speed_kmh = round(kts * 1.852, 2)
                        traces.append(NormalizationTraceItem(
                            field="velocity.speed_kmh",
                            original_field=alias,
                            original_value=container[alias],
                            normalized_value=speed_kmh,
                            conversion="knots_to_kmh_x1.852",
                        ))
                        break
                    except (ValueError, TypeError):
                        pass

        # Heading
        for alias in cls.HEADING_ALIASES:
            if alias in container and container[alias] is not None:
                try:
                    hdg = float(container[alias]) % 360.0
                    heading = round(hdg, 2)
                    traces.append(NormalizationTraceItem(
                        field="velocity.heading_deg",
                        original_field=alias,
                        original_value=container[alias],
                        normalized_value=heading,
                        conversion="degrees_mod_360",
                    ))
                    break
                except (ValueError, TypeError):
                    pass

        if speed_kmh is not None:
            speed_kmh = max(0.0, speed_kmh)
            return Velocity(speed_kmh=speed_kmh, heading_deg=heading), traces

        return None, traces
