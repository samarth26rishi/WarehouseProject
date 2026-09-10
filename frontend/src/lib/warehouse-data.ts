export type RiskLevel = "Low" | "Medium" | "High" | "Critical";

export type BehaviourKey =
  | "product_dropped"
  | "dragging"
  | "rough_handling"
  | "unstable_stacking"
  | "stepping_on_package"
  | "product_thrown"
  | "product_rolling";

export type BoundingBox = {
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
};

export type WarehouseEvent = {
  event_id: string;
  timestamp_video: string;
  camera_id: string;
  bay: string;
  objects: string[];
  behaviour: BehaviourKey;
  confidence: number;
  risk_level: RiskLevel;
  evidence: {
    clip_start: string;
    clip_end: string;
    frame_snapshot: string;
  };
  explanation: string;
  rules: string[];
  boxes: BoundingBox[];
};

export const behaviourLabels: Record<BehaviourKey, string> = {
  product_dropped: "Product dropped",
  dragging: "Dragging load",
  rough_handling: "Rough handling",
  unstable_stacking: "Unstable stacking",
  stepping_on_package: "Stepping on package",
  product_thrown: "Product thrown",
  product_rolling: "Product rolling",
};

export const riskLevels: RiskLevel[] = ["Low", "Medium", "High", "Critical"];

export const events: WarehouseEvent[] = [
  {
    event_id: "evt_00123",
    timestamp_video: "00:02:14",
    camera_id: "bay1_cam1",
    bay: "Bay 01",
    objects: ["person_2", "box_7"],
    behaviour: "product_dropped",
    confidence: 0.87,
    risk_level: "High",
    evidence: { clip_start: "00:02:11", clip_end: "00:02:17", frame_snapshot: "frame_00123.jpg" },
    explanation: "Box carried by person_2 lost contact with hands and fell approximately 1m before impact.",
    rules: ["Loss of hand-to-package contact", "Vertical displacement exceeded 0.6m", "Impact pose detected"],
    boxes: [
      { label: "person_2", x: 18, y: 28, width: 18, height: 47 },
      { label: "box_7 · dropped", x: 45, y: 61, width: 14, height: 16 },
    ],
  },
  {
    event_id: "evt_00124",
    timestamp_video: "00:04:48",
    camera_id: "bay3_cam2",
    bay: "Bay 03",
    objects: ["person_4", "pallet_2", "box_12"],
    behaviour: "unstable_stacking",
    confidence: 0.92,
    risk_level: "Critical",
    evidence: { clip_start: "00:04:45", clip_end: "00:04:54", frame_snapshot: "frame_00124.jpg" },
    explanation: "A tall stack leaned outside the stable footprint as the final box was placed.",
    rules: ["Stack height exceeded bay guideline", "Center of mass crossed pallet edge", "Lean persisted for 1.8 seconds"],
    boxes: [
      { label: "stack · unstable", x: 55, y: 25, width: 22, height: 52 },
      { label: "pallet_2", x: 50, y: 75, width: 35, height: 9 },
    ],
  },
  {
    event_id: "evt_00125",
    timestamp_video: "00:07:31",
    camera_id: "bay2_cam1",
    bay: "Bay 02",
    objects: ["person_1", "cart_3"],
    behaviour: "dragging",
    confidence: 0.81,
    risk_level: "Medium",
    evidence: { clip_start: "00:07:27", clip_end: "00:07:35", frame_snapshot: "frame_00125.jpg" },
    explanation: "A loaded cart moved with one wheel lifted, increasing the chance of a load shift.",
    rules: ["Wheel contact lost", "Load angle exceeded 12 degrees", "Motion continued for 2.4 seconds"],
    boxes: [
      { label: "person_1", x: 22, y: 30, width: 17, height: 48 },
      { label: "cart_3 · drag", x: 40, y: 49, width: 30, height: 28 },
    ],
  },
  {
    event_id: "evt_00126",
    timestamp_video: "00:11:06",
    camera_id: "bay1_cam1",
    bay: "Bay 01",
    objects: ["person_3", "box_19"],
    behaviour: "rough_handling",
    confidence: 0.76,
    risk_level: "High",
    evidence: { clip_start: "00:11:02", clip_end: "00:11:11", frame_snapshot: "frame_00126.jpg" },
    explanation: "Package acceleration and abrupt direction change indicate a rough set-down.",
    rules: ["Acceleration spike detected", "Set-down velocity above threshold", "Package orientation changed 38 degrees"],
    boxes: [
      { label: "person_3", x: 30, y: 22, width: 19, height: 54 },
      { label: "box_19 · rough", x: 47, y: 57, width: 17, height: 18 },
    ],
  },
  {
    event_id: "evt_00127",
    timestamp_video: "00:14:52",
    camera_id: "bay4_cam1",
    bay: "Bay 04",
    objects: ["person_5", "box_22"],
    behaviour: "stepping_on_package",
    confidence: 0.96,
    risk_level: "Critical",
    evidence: { clip_start: "00:14:49", clip_end: "00:14:57", frame_snapshot: "frame_00127.jpg" },
    explanation: "A foot entered the package footprint while the box was staged on the floor.",
    rules: ["Foot overlap with package footprint", "Contact sustained for 0.9 seconds", "Package marked fragile"],
    boxes: [
      { label: "person_5", x: 26, y: 20, width: 20, height: 58 },
      { label: "box_22 · contact", x: 45, y: 64, width: 22, height: 15 },
    ],
  },
  {
    event_id: "evt_00128",
    timestamp_video: "00:17:20",
    camera_id: "bay2_cam1",
    bay: "Bay 02",
    objects: ["person_1", "box_31"],
    behaviour: "product_dropped",
    confidence: 0.68,
    risk_level: "Low",
    evidence: { clip_start: "00:17:17", clip_end: "00:17:24", frame_snapshot: "frame_00128.jpg" },
    explanation: "A small parcel tipped from a low platform; no visible impact damage was observed.",
    rules: ["Object left platform boundary", "Drop distance below 0.3m", "No visible deformation"],
    boxes: [
      { label: "person_1", x: 34, y: 27, width: 17, height: 48 },
      { label: "box_31 · low drop", x: 54, y: 64, width: 14, height: 14 },
    ],
  },
];

export const shiftStats = {
  totalEvents: 38,
  highRisk: 7,
  commonBehaviour: "Product dropped",
  busiestBay: "Bay 01",
  trend: "+12%",
};

export const riskDistribution = [
  { label: "Low", value: 14, percent: 37 },
  { label: "Medium", value: 11, percent: 29 },
  { label: "High", value: 8, percent: 21 },
  { label: "Critical", value: 5, percent: 13 },
];

export const behaviourDistribution = [
  { label: "Product dropped", value: 12 },
  { label: "Rough handling", value: 9 },
  { label: "Unstable stacking", value: 7 },
  { label: "Dragging load", value: 6 },
  { label: "Stepping on package", value: 4 },
];

export const assistantResponses: Record<string, string> = {
  "Show me all high-risk handling events from today": "I found 7 high-risk events today. The most recent pattern is rough set-downs in Bay 01, with two events that would benefit from a quick coaching review.",
  "What were the most common risky behaviours this shift?": "Product drops lead this shift with 12 observations, followed by rough handling with 9. The current trend is useful for a process conversation, not an individual scorecard.",
  "Which bay had the most risky events?": "Bay 01 has the most observations at 11, including the 00:02:14 product drop. Bay 03 follows with 9 observations, mostly stacking stability.",
  "Why was this event classified as high risk?": "This event was classified as high risk because hand-to-package contact was lost, the box moved more than 0.6m vertically, and an impact pose was detected. The label describes potential damage risk; it does not claim damage occurred.",
};