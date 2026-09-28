# 17 — UI Component and Route Map

## 1. Routes

Suggested Next.js App Router structure:

```text
/
 /projects/new
 /projects/[projectId]
 /projects/[projectId]/overview
 /projects/[projectId]/goals/[goalId]
 /projects/[projectId]/processes/[processId]
 /projects/[projectId]/stages/[stageId]
 /projects/[projectId]/concepts/[conceptId]
 /projects/[projectId]/operations/[operationId]
 /projects/[projectId]/learn/[goalId]
 /projects/[projectId]/sources
 /projects/[projectId]/versions
 /projects/[projectId]/settings
 /settings
```

## 2. App shell

Components:

```text
AppShell
├─ GlobalSidebar
├─ ProjectSidebar
├─ TopBar
├─ Breadcrumbs
└─ MainContent
```

## 3. Project overview components

```text
ProjectOverview
├─ ProjectHeader
├─ MentalModelCard
├─ GoalMap
│  └─ GoalCard[]
├─ SharedFoundationCard
├─ LearningProgressCard
└─ RecentActivity
```

## 4. Process components

```text
ProcessView
├─ ProcessHeader
├─ ProcessRail
│  ├─ FoundationNode
│  ├─ StageNode[]
│  └─ GoalNode
├─ ProcessOutcome
├─ PracticePreview
└─ ExtensionBranches
```

`ProcessRail` should be implemented without requiring React Flow.

## 5. Stage components

```text
StageView
├─ StageHeader
├─ LocalGoalPanel
├─ WhyItExists
├─ ConceptList
├─ OperationList
├─ ExamplePanel
├─ BranchPanel
├─ ImplementationDetails (collapsed)
├─ EvidencePanel (collapsed)
└─ RefineActions
```

## 6. Learn Mode components

```text
LearnLayout
├─ LearnHeader
├─ StageProgressRail
├─ LearnStageContent
├─ ConceptInlineCards
├─ OperationInlineCards
├─ PracticePanel
├─ CheckpointPanel
└─ LearnNavigation
```

Learn Mode should minimize edit controls and project-management noise.

## 7. Generation components

```text
GenerationDrawer
├─ RunStatus
├─ HarnessStepList
├─ WarningList
├─ CancelButton
└─ ResultActions
```

## 8. Source components

```text
SourceManager
├─ AddSourceMenu
├─ UploadDropzone
├─ UrlSourceForm
├─ TextSourceForm
├─ SourceList
│  └─ SourceRow[]
└─ SourcePreview
```

## 9. Editing components

Reusable:

```text
EditableField
AIRefineButton
CandidateDiff
PublishDialog
UnsavedChangesBadge
```

## 10. State management

Use server state via TanStack Query.

Use local React state for:

- open/collapsed panels,
- temporary form content,
- local edit buffers.

Do not introduce Redux unless a later requirement proves necessary.

## 11. Rendering rule

All COP artifact rendering should go through typed selectors/adapters.

Do not scatter direct raw JSON access across components.

Example:

```text
artifactSelectors.getGoal(id)
artifactSelectors.getStagesForProcess(id)
artifactSelectors.getConceptsForStage(id)
```

This protects the UI from schema evolution.
