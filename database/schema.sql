-- Supabase/PostgreSQL schema
-- Run this file in Supabase SQL Editor.
-- The FastAPI application can also create these tables automatically,
-- but keeping SQL in GitHub documents the cloud data model.

create table if not exists sensor_readings (
  id bigserial primary key,
  device_id varchar(100) not null,
  soil_moisture double precision not null check (soil_moisture between 0 and 100),
  temperature double precision not null,
  humidity double precision not null check (humidity between 0 and 100),
  light double precision not null,
  recorded_at timestamptz not null default now()
);

create index if not exists idx_sensor_device_time
on sensor_readings(device_id, recorded_at desc);

create table if not exists plant_settings (
  id bigserial primary key,
  moisture_threshold double precision not null default 35,
  temperature_alert double precision not null default 38,
  humidity_alert double precision not null default 25,
  watering_seconds integer not null default 10,
  cooldown_seconds integer not null default 60
);

create table if not exists watering_events (
  id bigserial primary key,
  device_id varchar(100) not null,
  reason varchar(255) not null,
  duration_seconds integer not null,
  status varchar(30) not null default 'completed',
  started_at timestamptz not null default now()
);

create table if not exists alerts (
  id bigserial primary key,
  severity varchar(20) not null,
  message text not null,
  created_at timestamptz not null default now(),
  acknowledged boolean not null default false
);

create table if not exists device_states (
  device_id varchar(100) primary key,
  pump_on boolean not null default false,
  last_seen timestamptz not null default now()
);
