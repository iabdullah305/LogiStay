// =========================
// Enums
// =========================
Enum owner_type {
  COMPANY
  DRIVER
  EXTERNAL
}

Enum assignment_role {
  PRIMARY
  ALTERNATE
  SHARED
}

Enum vehicle_status {
  Available
  Assigned
  Maintenance
}

Enum shift_status {
  PLANNED
  CONFIRMED
  CANCELLED
  COMPLETED
}

Enum leg_type {
  OUTBOUND
  RETURN
}

Enum coverage_role {
  PRIMARY
  ASSIST
  RETURN_ONLY
  DROP_ONLY
}

Enum contract_type {
  KAFALA_SALARY
  FREELANCE_SELF_CAR
  HYBRID_SALARY_PLUS_VEH_RENT
}

Enum pay_party {
  COMPANY
  DRIVER
  SHARED
}

// NEW: Run shift as a series with period and repetition
Enum series_status {
  ACTIVE
  PAUSED
  ENDED
}

// NEW: Station type within the leg (accommodation/branch/custom)
Enum stop_type {
  ACCOMMODATION
  BRANCH
  CUSTOM
}

// NEW: Action type at the station (pickup/drop-off/both)
Enum stop_action {
  PICKUP
  DROPOFF
  BOTH
}

// =========================
/* Core reference tables */
// =========================
Table cities {
  city_id integer [pk]
  name_ar varchar [not null]
  name_en varchar
  created_at timestamp
}

Table projects {
  project_id integer [pk]
  city_id integer [not null]
  name_ar varchar [not null]
  name_en varchar
  active boolean
  created_at timestamp

  Indexes {
    (city_id)
    (active)
  }
}

Table branches {
  branch_id integer [pk]
  project_id integer [not null]
  name varchar [not null]
  location_link varchar
  lat double
  lng double
  created_at timestamp

  Indexes {
    (project_id)
  }
}

Table accommodations {
  accommodation_id integer [pk]
  city_id integer [not null]
  name varchar [not null]
  address varchar
  lat double
  lng double
  created_at timestamp

  Indexes {
    (city_id)
  }
}

// Optional: project supervisors / contacts
Table supervisors {
  supervisor_id integer [pk]
  project_id integer [not null]
  full_name varchar [not null]
  phone varchar
  notes text
  created_at timestamp

  Indexes {
    (project_id)
  }
}

// =========================
/* Fleet & people */
// =========================
Table drivers {
  driver_id integer [pk]
  emp_code varchar
  full_name varchar [not null]
  phone_main varchar
  created_at timestamp

  Indexes {
    (emp_code) [unique]
  }
}

Table vehicles {
  vehicle_id integer [pk]
  plate_number varchar [not null, unique]
  make varchar
  model varchar
  type varchar // Sedan / Van / Bus ...
  capacity integer [not null] // vehicle seating capacity
  status vehicle_status
  created_at timestamp
}

Table vehicle_ownerships {
  ownership_id integer [pk]
  vehicle_id integer [not null]
  owner_type owner_type [not null] // COMPANY / DRIVER / EXTERNAL
  owner_driver_id integer // when owner_type = DRIVER
  owner_external_name varchar // when owner_type = EXTERNAL
  start_date date [not null]
  end_date date
  created_at timestamp

  Indexes {
    (vehicle_id)
    (owner_driver_id)
    (start_date, end_date)
  }
}

Table driver_vehicle_assignments {
  assignment_id integer [pk]
  driver_id integer [not null]
  vehicle_id integer [not null]
  role assignment_role [not null] // PRIMARY / ALTERNATE / SHARED
  start_ts timestamp [not null]
  end_ts timestamp
  created_at timestamp

  Indexes {
    (driver_id)
    (vehicle_id)
    (driver_id, start_ts)
    (vehicle_id, start_ts)
  }
}

Table driver_residency {
  residency_id integer [pk]
  driver_id integer [not null]
  accommodation_id integer [not null]
  start_date date [not null]
  end_date date
  created_at timestamp

  Indexes {
    (driver_id)
    (accommodation_id)
    (start_date, end_date)
  }
}

// =========================
/* Operations (planning) */
// =========================

// NEW: Series of shifts with period and repetition (sets "how many days to work then stop/change")
Table shift_series {
  series_id integer [pk]
  project_id integer [not null]
  branch_id integer // Default gathering point for the series (optional)
  active_from date [not null] // Start of series validity
  active_to date              // End of validity (NULL = continuous)
  rrule varchar               // Example: FREQ=WEEKLY;BYDAY=SU,MO,...
  default_start_time time     // Default times
  default_end_time time
  default_required_passengers integer
  series_status series_status [not null, default: 'ACTIVE']
  notes text
  created_at timestamp

  Indexes {
    (project_id, active_from)
    (branch_id)
    (series_status)
  }
}

Table shifts {
  shift_id integer [pk]
  series_id integer              // NEW: Shift belongs to series (if any)
  project_id integer [not null]
  branch_id integer              // Meeting/intersection point for that day (may differ from series)
  shift_date date [not null]
  start_ts timestamp             // planned start
  end_ts timestamp               // planned end
  required_passengers_total integer
  status shift_status [not null, default: 'PLANNED']
  cancel_reason varchar          // NEW: Cancellation reason (when CANCELLED)
  is_exception boolean           // NEW: This day differs from series assumptions
  notes text
  created_at timestamp

  Indexes {
    (project_id, shift_date)
    (branch_id)
    (status)
    (series_id, shift_date)
  }
}

Table shift_legs {
  leg_id integer [pk]
  shift_id integer [not null]
  leg_type leg_type [not null] // OUTBOUND / RETURN
  required_passengers integer [not null, default: 0]
  start_point_id integer // optional: future ref to a Locations table
  end_point_id integer   // optional: future ref to a Locations table
  planned_start_ts timestamp
  planned_end_ts timestamp
  created_at timestamp

  Indexes {
    (shift_id)
    (leg_type)
  }
}

// NEW: Multiple stops per person (passes through multiple accommodations/branches with order and passenger quota)
Table shift_leg_stops {
  leg_stop_id integer [pk]
  leg_id integer [not null]
  seq integer [not null]                 // Passing order
  stop_type stop_type [not null]         // ACCOMMODATION / BRANCH / CUSTOM
  stop_action stop_action [not null, default: 'PICKUP'] // Pickup/Drop-off
  accommodation_id integer               // When stop_type = ACCOMMODATION
  branch_id integer                      // When stop_type = BRANCH
  custom_name varchar                    // When stop_type = CUSTOM
  custom_address varchar
  lat double
  lng double
  planned_passengers integer             // Expected number of passengers from/to this stop
  planned_arrival_ts timestamp
  planned_departure_ts timestamp
  notes text
  created_at timestamp

  Indexes {
    (leg_id, seq)
    (accommodation_id)
    (branch_id)
  }
}

Table shift_coverage {
  coverage_id integer [pk]
  leg_id integer [not null]
  assignment_id integer [not null] // (driver + vehicle) at that time window
  coverage_role coverage_role [not null] // PRIMARY / ASSIST / RETURN_ONLY / DROP_ONLY
  planned_capacity_committed integer [not null] // seats committed from this crew
  created_at timestamp

  Indexes {
    (leg_id)
    (assignment_id)
  }
}

// =========================
/* Commercial model (optional now) */
// =========================
Table contracts {
  contract_id integer [pk]
  driver_id integer [not null]
  type contract_type [not null] // KAFALA_SALARY / FREELANCE_SELF_CAR / HYBRID_SALARY_PLUS_VEH_RENT
  base_salary decimal(12,2)
  vehicle_rent_paid_by pay_party // COMPANY / DRIVER / SHARED
  iqama_fees_paid_by pay_party
  start_date date [not null]
  end_date date
  created_at timestamp

  Indexes {
    (driver_id)
    (type)
    (start_date, end_date)
  }
}

// =========================
// Relationships
// =========================
Ref: projects.city_id > cities.city_id
Ref: branches.project_id > projects.project_id
Ref: accommodations.city_id > cities.city_id
Ref: supervisors.project_id > projects.project_id

Ref: vehicle_ownerships.vehicle_id > vehicles.vehicle_id
Ref: vehicle_ownerships.owner_driver_id > drivers.driver_id

Ref: driver_vehicle_assignments.driver_id > drivers.driver_id
Ref: driver_vehicle_assignments.vehicle_id > vehicles.vehicle_id

Ref: driver_residency.driver_id > drivers.driver_id
Ref: driver_residency.accommodation_id > accommodations.accommodation_id

// Series relations
Ref: shift_series.project_id > projects.project_id
Ref: shift_series.branch_id > branches.branch_id

// Shifts relations
Ref: shifts.series_id > shift_series.series_id
Ref: shifts.project_id > projects.project_id
Ref: shifts.branch_id > branches.branch_id

Ref: shift_legs.shift_id > shifts.shift_id

// NEW: Stops relations
Ref: shift_leg_stops.leg_id > shift_legs.leg_id
Ref: shift_leg_stops.accommodation_id > accommodations.accommodation_id
Ref: shift_leg_stops.branch_id > branches.branch_id

Ref: shift_coverage.leg_id > shift_legs.leg_id
Ref: shift_coverage.assignment_id > driver_vehicle_assignments.assignment_id

Ref: contracts.driver_id > drivers.driver_id