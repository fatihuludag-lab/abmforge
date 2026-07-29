# Simulation Semantics V1

## Status

**Document status:** Current alpha contract and target semantic decisions
**Applies to:** ABMForge `0.3.0a1` development line
**Stability:** Provisional until the public-alpha semantic blockers are resolved
**Audience:** Model authors, framework contributors, reviewers, and plugin authors

This document defines the observable simulation semantics of ABMForge.

It distinguishes between:

1. **Current behavior** — behavior implemented by the current runtime.
2. **Target contract** — behavior ABMForge intends to guarantee after the corresponding semantic corrections are implemented.
3. **Unsupported behavior** — behavior that users must not currently assume.

This distinction is important because documenting an existing implementation does not automatically make every existing behavior desirable or stable.

Related documentation:

* [Scheduling](scheduling.md)
* [Delayed Events](delayed-events.md)
* [Agent Lifecycle](agent-lifecycle.md)
* [Model Lifecycle](model-lifecycle.md)
* [Recording Data](recording.md)
* [Reproducibility Tiers](reproducibility-tiers.md)
* [Replay and Snapshots](replay.md)

---

## 1. Scope

Simulation semantics include:

* model step and time progression;
* event processing order;
* agent activation order;
* agent creation and removal visibility;
* simultaneous and staged state transitions;
* recording time;
* stop-condition evaluation;
* random-number ownership;
* failure and partial-step behavior.

This document does not define:

* domain-specific model validity;
* calibration or statistical inference methods;
* continuous-time simulation;
* distributed simulation;
* full checkpoint/resume;
* executable event replay;
* bit-identical results across platforms or dependency versions.

---

## 2. Terminology

### Step

A **step** is one completed iteration of the fixed-step model loop.

The model exposes the completed-step count as:

```python
model.steps
```

The initial value is `0`.

### Simulation time

Simulation time is exposed as:

```python
model.time
```

The initial value is `0.0`.

The current fixed-step runner increases time by `1.0` after each completed model step.

### Tick

In the current fixed-step execution profile, a **tick** corresponds to one model step and one `1.0` increase in simulation time.

ABMForge does not currently provide a separate tick object.

### Activation pass

An **activation pass** is one scheduler or collection bulk-operation call over a selected set of agents.

Examples:

```python
model.agents.do("step")
model.agents.shuffle_do("step")
model.scheduler.step()
```

### Phase

A **phase** is an ordered part of a model iteration, such as event processing, model activation, recording, or stop-condition evaluation.

### Eligible agent

An **eligible agent** is an agent permitted to receive a callback in a particular activation pass or stage.

Eligibility depends on:

* membership policy;
* lifecycle state;
* when the activation snapshot was created;
* the selected scheduler.

### Current state and next state

For synchronous models:

* **current state** is the state visible during the decision phase;
* **next state** is pending state intended to become current during a later commit phase.

The current runtime does not automatically isolate current and next state.

---

## 3. Current fixed-step model loop

### 3.1 Current runtime order

For each requested model step, the current runtime performs:

```text
1. Process events due at the current model time
2. Call model.step()
3. Increment model.steps by 1
4. Increment model.time by 1.0
5. Collect registered model and agent observations
```

Equivalent pseudocode:

```python
for _ in range(requested_steps):
    if not model.running:
        break

    model.events.process_due(time=model.time)
    model.step()

    model.steps += 1
    model.time += 1.0

    model.record.collect()
```

### 3.2 Consequences

Under the current implementation:

* events due at time `t` are processed before `model.step()` for time `t`;
* observations are collected after the model step;
* observations use the incremented `steps` and `time` values;
* the first automatic post-step observation is associated with step `1` and time `1.0`;
* no automatic time-zero observation is collected;
* an exception during event processing, `model.step()`, or recording marks the model as failed;
* if `model.stop()` is called inside `model.step()`, the current loop still increments the counters and performs the post-step recording for that iteration unless an exception interrupts execution.

### 3.3 Target fixed-step phase contract

The target fixed-step execution profile will use explicit named phases:

```text
TICK_START
→ PRE_STEP_EVENTS
→ ACTIVATION
→ COUNTER_ADVANCE
→ POST_STEP_OBSERVATION
→ STOP_EVALUATION
→ TICK_END
```

The exact placement of post-step events, if introduced, must be specified by a later version of this contract.

No plugin or scheduler may silently reorder these phases.

---

## 4. Event-time semantics

### 4.1 Current fixed-step contract

The built-in fixed-step execution profile accepts only finite,
integer-valued event ticks.

Events may be scheduled using:

```python
model.events.schedule_at(time, callback=...)
model.events.schedule_after(delay, callback=...)
```

Accepted values include integers and integer-valued floats:

```python
model.events.schedule_at(2, callback=callback)
model.events.schedule_at(2.0, callback=callback)
model.events.schedule_after(1, callback=callback)
model.events.schedule_after(1.0, callback=callback)
```

Accepted values are normalized to `float` for queue storage and ordering.

The current contract rejects:

- fractional absolute event times;
- fractional delays;
- Boolean values;
- strings and objects accepted only through implicit numeric coercion;
- non-finite values;
- negative delays;
- absolute event times earlier than the current model time.

A rejected scheduling request does not:

- consume an event identifier;
- create a pending event;
- write an event record.

### 4.2 Execution timing

For an event scheduled at tick `t`, the fixed-step runner processes the
event before `model.step()` when `model.time == t`.

Pending events are ordered by:

```text
event tick
-> priority
-> insertion sequence
-> event identifier
```

`process_due(time=t)` executes pending events whose scheduled tick is less
than or equal to `t`.

Because fractional event times are rejected during scheduling, the built-in
runner cannot silently delay a fractional event until the next integer
model time.

The fixed-step profile is not a continuous-time or general discrete-event
simulation engine.

### 4.3 Same-tick event behavior

During `process_due(time=t)`, an event callback may schedule another event
for tick `t`.

Because the queue continues draining while due events remain, the newly
scheduled event may execute during the same event-processing call.

An event scheduled for the current tick from inside `model.step()` is
created after the pre-step event drain. It therefore executes during a
later event-processing phase.

This callback-context distinction is current behavior.

### 4.4 Remaining event-system work

Future event-system revisions should:

- distinguish event creation, requested execution, and actual execution
  timestamps in event records;
- define a resource-safety policy for recursive same-tick scheduling;
- formalize any post-step event phase;
- version the event-time and event-phase policies in run metadata;
- use a separate experimental profile for hybrid or continuous-time
  simulation.

---

## 5. Agent collection bulk operations

### 5.1 Shared callback-time eligibility

All built-in collection bulk operations and schedulers use a shared
callback-time activation eligibility rule.

A candidate agent is eligible immediately before a callback only when:

1. the collection still stores an object under the agent identifier;
2. the collection still stores the same object under that identifier;
3. the candidate agent remains alive.

Candidate agents are selected from a snapshot created at the beginning of the
activation pass or scheduler call.

Consequences:

- an agent added during the pass is deferred until a future pass;
- an agent removed before its turn is skipped;
- an agent marked not alive before its turn is skipped;
- if an agent is removed and replaced by another object with the same
  identifier, neither the removed snapshot object nor the newly added
  replacement is activated from that snapshot position;
- self-removal is safe and prevents callbacks in later phases or stages.

This rule prevents stale objects retained by an activation snapshot from being
called after removal.

### 5.2 `AgentCollection.do`

```python
model.agents.do("step")
```

`do()` creates an insertion-ordered candidate snapshot at the beginning of the
call.

Immediately before each callback, it revalidates object identity, current
collection membership, and lifecycle eligibility.

Insertion order remains part of the activation semantics.

### 5.3 `AgentCollection.shuffle_do`

```python
model.agents.shuffle_do("step")
```

`shuffle_do()` creates one candidate snapshot at the beginning of the call and
shuffles its indices using `model.rng`.

Immediately before each callback, it applies the same identity, membership,
and lifecycle eligibility checks as `do()`.

An agent removed after the permutation is generated is skipped when its turn
is reached.

### 5.4 Scope of the guarantee

Callback-time eligibility is not a complete lifecycle-cleanup operation.

Direct collection removal changes collection membership. Models requiring
world removal, owned-event cancellation, lifecycle-state changes, and
lifecycle records should use `Model.remove_agent(...)`.

---
## 6. Sequential activation

### 6.1 Current behavior

`SequentialActivation`:

1. creates an insertion-ordered candidate snapshot;
2. visits candidates in snapshot order;
3. revalidates object identity, collection membership, and `is_alive`
   immediately before each callback;
4. calls `agent.step()` only for eligible candidates.

An agent added after the candidate snapshot is created is deferred until a
future scheduler call.

An agent removed or marked not alive before its turn is skipped.

If a removed agent is replaced by another object using the same identifier,
the old object fails callback-time identity validation and the replacement is
not present in the original snapshot.

### 6.2 Scientific implication

Insertion order is part of the model semantics.

Researchers using sequential activation must document:

- how initial insertion order is determined;
- whether creation order has theoretical meaning;
- whether dynamic creation changes future activation priority;
- whether results are sensitive to activation order.

---

## 7. Random activation

### 7.1 Current behavior

`RandomActivation`:

1. creates a candidate snapshot from currently eligible agents;
2. generates a permutation using `model.rng`;
3. revalidates object identity, collection membership, and `is_alive`
   immediately before each callback;
4. calls `agent.step()` only for candidates that remain eligible.

Agents added after candidate selection are deferred.

Agents removed or marked not alive after the permutation is generated are
skipped when their turn is reached.

A replacement object using the same identifier is not activated from the
removed object's snapshot position.

### 7.2 Random-stream limitation

The scheduler currently uses the same model-level random-number generator
that model and agent behavior may also consume.

Therefore:

- activation order depends on earlier random draws;
- adding an unrelated random draw may change later activation order;
- a fixed seed does not provide component-independent random streams.

### 7.3 Target random-stream contract

A future random-stream contract will assign scheduler activation to a named
stream that is separate from behavior, event, initialization, and space
randomness.

Until then, random activation is reproducible only under an unchanged
random-draw history.

---

## 8. Simultaneous activation

### 8.1 Current behavior

`SimultaneousActivation`:

1. creates a candidate snapshot from currently eligible agents;
2. revalidates every candidate before its `step()` callback;
3. completes all eligible `step()` callbacks;
4. revalidates every candidate before its optional `advance()` callback;
5. calls `advance()` only when the candidate remains eligible and defines
   that method.

An agent removed before its decision turn does not receive `step()`.

An agent removed during the decision phase does not receive `advance()`.

An agent added during the scheduler call is deferred until a future call.

The scheduler does not currently require every participating agent to
implement `advance()`.

The scheduler also does not prevent `step()` from directly changing current
state.

### 8.2 Current guarantee

```text
all eligible step() callbacks
-> all eligible advance() callbacks
```

Callback-time identity, membership, and lifecycle eligibility are checked in
both phases.

The current implementation does not guarantee:

- immutable current-state views;
- automatic next-state buffers;
- order-independent decision calculations;
- atomic model-wide state commit;
- an error when `advance()` is missing.

### 8.3 Required user pattern

Synchronous models should use explicit pending state:

```python
class ExampleAgent(Agent):
    def step(self) -> None:
        self.next_value = self.compute_next_value()

    def advance(self) -> None:
        self.value = self.next_value
```

Directly changing `self.value` in `step()` may expose the updated value to
agents activated later in the same decision phase.

### 8.4 Remaining public-alpha work

The target strict simultaneous contract will:

- require an explicit two-phase capability;
- fail early when an eligible agent lacks the required commit method;
- preserve all-decision-before-any-commit ordering;
- define whether heterogeneous no-op commit adapters are supported;
- include a canonical synchronous reference-model test.

---

## 9. Staged activation

### 9.1 Current behavior

`StagedActivation`:

1. creates a candidate snapshot from currently eligible agents;
2. retains that candidate snapshot for all declared stages;
3. executes stages in declared order;
4. optionally generates a separate permutation for each stage using
   `model.rng`;
5. revalidates object identity, collection membership, and `is_alive`
   immediately before every stage callback;
6. calls optional `before_stage(stage)` and `after_stage(stage)` model hooks.

### 9.2 Lifecycle visibility

Under the current implementation:

- agents added after candidate selection do not participate in the current
  scheduler call;
- agents removed during an earlier stage are skipped in later stages;
- agents removed before their turn in the current stage are skipped;
- agents marked not alive are skipped;
- a same-identifier replacement is deferred because it is not part of the
  original candidate snapshot;
- each shuffled stage may use a different activation order;
- declared stage methods must exist and be callable.

### 9.3 Research reporting requirements

A staged model should document:

- stage names and order;
- whether stage-level shuffling is enabled;
- which state changes are visible to later stages;
- whether creation or removal may occur during stages;
- what the model-level stage hooks do;
- which random stream controls stage order.

---

## 10. Agent creation and removal

### 10.1 Same-pass creation

Built-in activation paths create a candidate snapshot at the beginning of
their activation pass or scheduler call.

An agent added after that snapshot is created is registered immediately but
is not activated until a future pass.

This guarantee applies to:

- `AgentCollection.do()`;
- `AgentCollection.shuffle_do()`;
- `SequentialActivation`;
- `RandomActivation`;
- `SimultaneousActivation`;
- `StagedActivation`.

### 10.2 Same-pass removal

An agent removed before its next callback becomes immediately ineligible.

Eligibility requires:

- current membership in the collection;
- identity equality with the object currently stored under the identifier;
- a living lifecycle state.

This prevents stale candidate references from being called after removal.

### 10.3 Same-identifier replacement

If an agent is removed and a new object is inserted under the same identifier
during an activation pass:

- the removed object fails the callback-time identity check;
- the replacement object is absent from the original candidate snapshot;
- neither object is activated from the stale snapshot position;
- the replacement becomes eligible in a future pass.

### 10.4 Collection removal versus model removal

Direct `AgentCollection.remove(...)` changes collection membership.

`Model.remove_agent(...)` is the model-level lifecycle operation and should be
used when the model also requires:

- world or space cleanup;
- lifecycle-state changes;
- owned-event cancellation;
- lifecycle recording.

### 10.5 Remaining lifecycle work

Removal-aware activation is now part of the runtime guarantee, but further
public-alpha lifecycle work includes:

- uniform model-collection-space referential-integrity checks;
- consistent cleanup contracts across every built-in space type;
- an explicit repeated-removal policy;
- persistent identity rules for recorded data;
- conformance tests for custom schedulers and spaces.

---

## 11. Recording semantics

### 11.1 Current automatic recording

Registered model and agent observations are collected after:

```text
model.step()
→ model.steps += 1
→ model.time += 1.0
```

Therefore, an automatic record containing:

```text
step = 1
time = 1.0
```

describes the post-step state after the first completed model step.

### 11.2 Time-zero observations

The current model loop does not automatically collect an initial time-zero observation.

Users requiring a baseline observation must collect it explicitly or use a future recording profile that declares an initialization phase.

### 11.3 Frequency

The `every` option is evaluated using the current completed-step count.

For example, `every=2` records at completed steps divisible by `2`.

### 11.4 Conditional recording

A `when` predicate is evaluated at recording time, after the model step and counter increment.

Agent-level `where` predicates are evaluated for agents present in the collection at recording time.

### 11.5 Event and lifecycle record times

Event and lifecycle transitions are currently recorded using the model’s current `steps` and `time` when the recorder method is called.

The event record does not by itself distinguish:

* when the event was created;
* when it was scheduled to run;
* when it became due;
* when it actually executed.

### 11.6 Target observation contract

A future observation schema will explicitly declare:

* observation phase;
* variable type;
* unit;
* missing-value policy;
* aggregation level;
* whether the observation represents pre-step, post-step, initialization, or finalization state.

---

## 12. Stop-condition semantics

### 12.1 Direct model stop

Calling:

```python
model.stop(reason)
```

sets:

```text
running = false
status = stopped
stop_reason = reason
```

A stopped model cannot be restarted through the current fixed-step runner.

### 12.2 Scenario stop condition

A scenario-level `stop_when` callback is currently evaluated:

1. before each requested model step;
2. after each completed one-step model execution.

If the callback is true before the first step:

* the model is stopped;
* no model step is executed for that iteration.

If the callback becomes true after a completed step:

* the step has already run;
* counters have already advanced;
* post-step recording has already occurred;
* the model is then marked stopped.

### 12.3 Outcome interpretation

`stopped` means execution ended because of an explicit model or scenario condition.

It does not inherently mean:

* failed;
* invalid;
* incomplete;
* excluded from analysis.

Execution status and scientific analysis eligibility must be handled as separate concepts.

---

## 13. Failure semantics

### 13.1 Current model-loop failure

An exception during the fixed-step loop:

* stops execution;
* sets the model status to failed;
* re-raises the exception.

The model may already contain partial state changes from:

* processed events;
* partially completed activation;
* the model step;
* partially completed recording.

### 13.2 No automatic rollback

The current runtime does not provide transactional rollback of a partially executed simulation step.

Users must not assume that a failed step leaves the model at the previous completed state.

### 13.3 Target failure contract

Future versions should record:

* failure phase;
* current step and time;
* active scheduler stage;
* related agent or event identity where available;
* whether records were committed;
* whether the run is retryable;
* whether the artifact is complete, partial, or corrupt.

---

## 14. Randomness and determinism

### 14.1 Current generator

Each model creates one NumPy random-number generator from the model seed.

The model, schedulers, and user behavior may consume this shared generator.

### 14.2 Current same-seed guarantee

The current safe claim is:

> Under the same code, environment, initial state, execution order, and random-draw history, the same seed is intended to reproduce the same model-level random sequence.

A seed alone does not guarantee:

* independent scheduler and agent streams;
* identical results after unrelated random draws are added;
* control of Python’s `random` module;
* control of third-party-library randomness;
* identical results across operating systems;
* identical results across Python, NumPy, or dependency versions;
* bit-identical archives.

### 14.3 Target random-stream contract

The target design will use versioned named streams for at least:

```text
initialization
behavior
activation
events
space
```

The manifest and snapshot contracts must record the stream-derivation version and supported stream states.

---

## 15. Current guarantee matrix

| Topic | Current guarantee | Not currently guaranteed |
|---|---|---|
| Fixed-step time | `steps += 1` and `time += 1.0` after a completed model step | Variable-step or continuous-time execution |
| Event times | Finite integer-valued ticks with strict input validation | Hybrid or continuous-time execution |
| Event ordering | Time, priority, sequence, and event identifier | Context-independent same-time scheduling semantics |
| Collection `do()` | Insertion-order candidate snapshot with callback-time identity, membership, and liveness validation | Activation of agents added during the current pass |
| Collection `shuffle_do()` | Seeded candidate-snapshot permutation with callback-time eligibility validation | Independent scheduler RNG stream |
| Sequential activation | Insertion-order candidate snapshot with callback-time eligibility validation | Dynamic additions during the current pass |
| Random activation | Initial eligible snapshot, seeded permutation, and callback-time eligibility validation | Independence from behavior RNG draws |
| Simultaneous activation | All eligible `step()` callbacks before eligible `advance()` callbacks, with validation in both phases | Automatic state isolation or mandatory `advance()` |
| Staged activation | Declared stage order, optional per-stage shuffle, and validation before every stage callback | Dynamic additions during the current scheduler call |
| Same-pass removal | Removed, replaced, or non-living candidates are skipped before their next callback | Complete lifecycle cleanup from direct collection removal |
| Same-pass creation | Newly added agents are deferred until a future pass | Immediate participation in the current candidate snapshot |
| Recording | Post-step observations use incremented counters | Automatic time-zero observation |
| Scenario stop | Stop condition is checked before and after one-step execution | Automatic scientific analysis eligibility |
| Failure | Failed status is recorded and the exception is raised | Transactional rollback of a partial step |
| Snapshot | Selected model, agent, and RNG state is captured | Full world, scheduler, event callback, and recorder restoration |
| Reproducibility | Conditional same-seed rerun under unchanged execution history | Cross-platform or cross-version equality |

## 16. Public-alpha semantic blockers

The following issues must still be resolved before the fixed-step execution
profile can be treated as public-alpha semantics:

1. Valid stopped runs may be excluded from default analysis reports.
2. Simultaneous activation does not require a complete two-phase agent
   contract.
3. Scheduler randomness and agent behavior share one RNG stream.
4. Agent-collection-space lifecycle invariants are not uniformly enforced.
5. Canonical models lack sufficient scientific invariant and metamorphic
   tests.

Removal-aware callback eligibility and strict integer-tick event scheduling
are now part of the current runtime guarantee.

These remaining items concern correctness and scientific interpretation
rather than cosmetic API preferences.

## 17. Model-author responsibilities

Until the target contracts are implemented, model authors should:

1. document the scheduler and activation order;
2. use `Model.remove_agent(...)` when full lifecycle cleanup is required; direct collection removal changes collection membership only;
3. use finite integer event ticks in the fixed-step profile;
4. implement explicit current/next state buffers for simultaneous models;
5. record all random sources and avoid untracked third-party randomness;
6. define whether stopped runs are scientifically valid;
7. add model-specific conservation and transition invariants;
8. preserve source, input, dependency, seed, and environment information;
9. treat archive validation as artifact validation, not model validation;
10. treat generated ODD output as a draft requiring scholarly review.

---

## 18. Framework-contributor requirements

Any change to model execution must answer:

* Does the phase order change?
* Does agent eligibility change?
* Does event ordering change?
* Does the random-draw sequence change?
* Does the observation phase change?
* Can run status or stop reason change?
* Can existing model trajectories change?
* Does the snapshot or archive schema change?
* Is a migration or deprecation path required?
* Which characterization, invariant, property, or metamorphic tests prove the contract?

A change that modifies trajectories must be labeled as a scientific behavior change in the changelog and release notes.

---

## 19. Versioning policy

Simulation semantics are versioned independently from package marketing language.

A future manifest should record identifiers such as:

```text
execution_profile = fixed-step-v1
event_time_policy = integer-tick-v1
activation_lifecycle_policy = deferred-add-immediate-remove-v1
observation_policy = post-step-v1
rng_policy = named-streams-v1
```

Changing one of these policies may alter scientific results even when the public Python method signatures remain unchanged.

Such changes require:

* explicit release notes;
* regression tests;
* migration guidance;
* updated reference outputs;
* updated reproducibility metadata.

---

## 20. Summary

The current ABMForge runtime is best described as:

> A fixed-step Python ABM execution profile with finite integer event ticks,
> pre-step event processing, candidate-snapshot activation, callback-time
> identity and membership validation, deferred same-pass additions,
> immediate removal visibility, post-step observation, and multiple built-in
> activation strategies.

Fractional event times and implicit numeric coercion are rejected during
scheduling, preventing events from being silently executed later than
requested.

The remaining target public-alpha contract adds:

> Scientifically safe stopped-run reporting, strict two-phase simultaneous
> activation, named random streams, uniform model-collection-space lifecycle
> integrity, and scientifically verified reference models.

Researchers must report the exact ABMForge version or commit and the
model-specific scheduling, event-time, randomness, observation, and
lifecycle assumptions used in their studies.
