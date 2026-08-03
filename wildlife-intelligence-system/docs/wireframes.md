# UI Wireframes & Workflow Planning — Milestone 1

Low-fidelity wireframes for the screens delivered in Milestone 1. These map directly
to the routes implemented in `frontend/src/`.

## 1. Login

```
┌───────────────────────────────────────────┐
│  🌿 Wildlife Population Intelligence        │
│                                             │
│   Email      [_____________________]       │
│   Password   [_____________________]       │
│                                             │
│            [        Log in        ]        │
│                                             │
│   Don't have an account? Register →        │
└───────────────────────────────────────────┘
```

## 2. Register

```
┌───────────────────────────────────────────┐
│  Create account                            │
│   Full name  [_____________________]       │
│   Email      [_____________________]       │
│   Password   [_____________________]       │
│   Role       [ Researcher ▾ ]               │
│              (Researcher / Conservation     │
│               Officer / Forest Dept.)       │
│            [       Register       ]        │
└───────────────────────────────────────────┘
```

## 3. Shared shell (after login)

```
┌──────────────┬──────────────────────────────────────────────┐
│  🌿 WPI       │  Topbar: [Role badge]   [User name ▾ Logout] │
│  Dashboard    ├──────────────────────────────────────────────┤
│  Surveys      │                                              │
│  Monitoring   │              <route content>                 │
│    Sites      │                                              │
│  Devices      │                                              │
│  Observations │                                              │
│  (Admin only) │                                              │
│   Users        │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

## 4. Researcher Dashboard (landing)

```
┌──────────────────────────────────────────────────────────┐
│  Welcome back, Dr. Rao                                    │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ │
│  │ Active     │ │ Monitoring │ │ Uploads    │ │ Species    │ │
│  │ Surveys: 4 │ │ Sites: 12  │ │ this wk: 87│ │ tagged: 231│ │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ │
│                                                            │
│  My Surveys                              [+ New Survey]   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Name          Sites  Status    Start      End         │ │
│  │ Tiger Corridor  3     active   Jun 1      Aug 30       │ │
│  │ Bird Census A   5     active   Jul 10     Sep 10       │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## 5. Monitoring Sites — list + create

```
┌──────────────────────────────────────────────────────────┐
│  Monitoring Sites                       [+ Register Site] │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Site           Habitat    Protected Area   Devices    │ │
│  │ Ridge Camp A    Forest     Bandipur NP       2          │ │
│  │ Wetland North   Wetland    Kaziranga NP      1          │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘

New Site modal:
┌───────────────────────────────────────────┐
│  Register Monitoring Site                  │
│  Name          [_____________________]     │
│  Habitat type  [ Forest ▾ ]                 │
│  Protected area[_____________________]     │
│  Latitude      [__________]                 │
│  Longitude     [__________]                 │
│           [ Cancel ]  [ Save Site ]          │
└───────────────────────────────────────────┘
```

## 6. Surveys — create + detail

```
┌───────────────────────────────────────────┐
│  New Survey                                 │
│  Name          [_____________________]     │
│  Objective     [_____________________]     │
│  Start / End   [____] – [____]              │
│  Sites         [x] Ridge Camp A              │
│                [ ] Wetland North             │
│           [ Cancel ]  [ Create Survey ]      │
└───────────────────────────────────────────┘

Survey detail:
┌──────────────────────────────────────────────────────────┐
│  Tiger Corridor Survey            [Upload Media] [Edit]   │
│  Status: active   Sites: 3   Owner: Dr. Rao                │
│  ─ Observation history ──────────────────────────────────│
│  Date        Site           Type    Notes                  │
│  Jul 12       Ridge Camp A   image   pending analysis       │
│  Jul 12       Ridge Camp A   audio   pending analysis       │
└──────────────────────────────────────────────────────────┘
```

## 7. Devices (camera traps / audio sensors)

```
┌──────────────────────────────────────────────────────────┐
│  Devices                                  [+ Add Device]  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Device ID   Type         Site           Status        │ │
│  │ CT-014       camera_trap  Ridge Camp A   active         │ │
│  │ AS-002       audio_sensor Wetland North  active         │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## 8. Admin — Users & roles

```
┌──────────────────────────────────────────────────────────┐
│  Users                                     [+ Invite User]│
│  Name          Email                Role          Status  │
│  Dr. Rao        rao@ngo.org          researcher    active  │
│  A. Fernandes   fernandes@forest.gov forest_dept    active  │
└──────────────────────────────────────────────────────────┘
```

## Workflow map (screens → API)

| Screen                | Backend endpoint(s)                                  |
|------------------------|-------------------------------------------------------|
| Login / Register       | `POST /auth/login`, `POST /auth/register`             |
| Dashboard summary       | `GET /surveys/me/summary`                             |
| Monitoring Sites list   | `GET/POST /monitoring-sites`                          |
| Devices list            | `GET/POST /devices`                                   |
| Surveys list/detail     | `GET/POST /surveys`, `GET /surveys/{id}`               |
| Upload media             | `POST /surveys/{id}/media`                             |
| Observation history      | `GET /surveys/{id}/observations`                        |
| Admin users              | `GET/POST/PATCH /users`                                 |
