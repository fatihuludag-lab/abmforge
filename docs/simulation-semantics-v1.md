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

### 4.1 Current behavior

The event queue currently accepts finite numeric event times.

Events may be scheduled using:

```python
model.events.schedule_at(time, callback=...)
model.events.schedule_after(delay, callback=...)
```

Pending events are ordered by:

```text
event time
→ priority
→ insertion sequence
→ event identifier
```

Lower tuple values execute first.

`process_due(time=t)` executes pending events whose scheduled time is less than or equal to `t`.

### 4.2 Current fractional-time limitation

The queue accepts fractional event times, but the fixed-step model runner advances time only by `1.0`.

For example, an event scheduled at `0.5` is not guaranteed to execute at simulation time `0.5`. The fixed-step runner does not advance the model clock to the next pending event time.

Therefore, the current fixed-step execution profile must not be treated as a continuous-time or general discrete-event simulation engine.

### 4.3 Same-time event behavior

During `process_due(time=t)`, an event callback may schedule another event due at `t`.

Because the queue is drained while due events remain, that newly scheduled event may execute during the same event-processing call.

By contrast, an event scheduled for the current time from inside `model.step()` is created after the pre-step event drain. It will not execute until a later event-processing phase.

This callback-context difference is current behavior, not yet a stable target guarantee.

### 4.4 Target public-alpha contract

The public-alpha fixed-step profile will use non-negative integer event ticks.

Under the target contract:

* fractional absolute event times will be rejected;
* fractional delays will be rejected;
* negative, non-finite, and past event times will be rejected;
* every event will expose its requested execution tick;
* event records will distinguish scheduling time from execution time;
* same-tick scheduling behavior will be defined for every phase;
* recursive same-tick scheduling will have a resource-safety policy.

A future event-driven or hybrid execution profile must use a separate, explicitly experimental clock contract.

---

## 5. Agent collection bulk operations

### 5.1 `AgentCollection.do`

Current behavior:

```python
model.agents.do("step")
```

creates an insertion-ordered list of agents at the start of the call and invokes the selected method on every object in that list.

The current implementation does not re-check:

* whether the agent is still in the collection;
* whether the stored object for that identifier is still the same object;
* whether the agent is alive.

Consequences:

* an agent added during the pass is not included in that pass;
* an agent removed during the pass may still receive its callback later in the same pass;
* collection removal and lifecycle removal may produce different effects if lifecycle state is not updated consistently.

### 5.2 `AgentCollection.shuffle_do`

Current behavior:

```python
model.agents.shuffle_do("step")
```

creates one agent list at the start of the call, shuffles its indices using `model.rng`, and calls the method on every object in the shuffled list.

The same membership and lifecycle limitations as `do()` apply.

### 5.3 Target collection contract

The target contract is:

1. Candidate agents are selected at the start of the activation pass.
2. Agents added during the pass are deferred until a future pass.
3. Before each callback, the collection re-checks that:

   * the agent is alive;
   * the agent is still a member;
   * the collection still stores the same object under that identifier.
4. An agent removed before its turn does not receive a later callback in that pass.
5. Self-removal is safe.
6. Collection bulk operations and equivalent scheduler policies follow the same lifecycle rules.

This target behavior requires a runtime change and must not be assumed until the corresponding tests pass.

---

## 6. Sequential activation

### 6.1 Current behavior

`SequentialActivation`:

1. creates a list from the current model agent collection;
2. visits agents in collection insertion order;
3. checks `is_alive` before calling `agent.step()`.

An agent added after the list is created is not activated in the current pass.

An agent whose `is_alive` value becomes false before its turn is skipped.

Current membership is not independently revalidated before the callback.

### 6.2 Scientific implication

Insertion order is part of the model semantics.

Researchers using sequential activation must document:

* how initial insertion order is determined;
* whether creation order has theoretical meaning;
* whether dynamic creation changes future activation priority;
* whether results are sensitive to order.

---

## 7. Random activation

### 7.1 Current behavior

`RandomActivation`:

1. selects agents that are alive when the activation list is created;
2. generates a permutation using `model.rng`;
3. checks `is_alive` again immediately before calling `agent.step()`.

Agents added after the activation list is created are deferred.

Agents marked not alive before their turn are skipped.

### 7.2 Random-stream limitation

The current scheduler uses the same model-level random-number generator that user model behavior may also use.

Therefore:

* activation order depends on the prior random draws made by the model and its agents;
* adding an unrelated random draw may change later activation order;
* a fixed seed does not provide component-independent random streams.

### 7.3 Target contract

A future random-stream contract will assign activation randomness to a named scheduler stream separate from agent behavior and other components.

Until that contract is implemented, users must treat random activation as deterministic only under an unchanged random-draw history.

---

## 8. Simultaneous activation

### 8.1 Current behavior

`SimultaneousActivation`:

1. creates a list of agents that are alive at the beginning of the scheduler call;
2. calls `step()` on each agent still marked alive;
3. calls `advance()` on each agent still marked alive and having an `advance` attribute.

The current scheduler does not require every agent to implement `advance()`.

The current scheduler does not prevent `step()` from changing current state directly.

### 8.2 What is currently guaranteed

The current implementation guarantees call-pass ordering:

```text
all eligible step() calls
→ all eligible advance() calls
```

It does not guarantee:

* immutable current-state views;
* automatic next-state buffers;
* order-independent decisions;
* atomic model-wide state commit;
* an error when `advance()` is missing.

### 8.3 Required user pattern

Models using the current implementation should use explicit pending state:

```python
class ExampleAgent(Agent):
    def step(self) -> None:
        self.next_value = self.compute_next_value()

    def advance(self) -> None:
        self.value = self.next_value
```

Directly changing `self.value` in `step()` may expose the new value to agents activated later in the same pass.

### 8.4 Target public-alpha contract

The target contract will:

* require an explicit two-phase capability for all participating agents;
* fail early when an eligible agent lacks the required commit method;
* preserve the rule that all decision calls finish before any commit call;
* define add/remove eligibility for both phases;
* document whether heterogeneous no-op commit adapters are supported;
* provide a canonical synchronous reference-model test.

---

## 9. Staged activation

### 9.1 Current behavior

`StagedActivation`:

1. selects agents that are alive at the beginning of the scheduler call;
2. retains that initial candidate list for all stages;
3. executes stages in the declared order;
4. optionally produces a separate random permutation for each stage using `model.rng`;
5. checks `is_alive` before each stage callback;
6. calls optional model-level `before_stage(stage)` and `after_stage(stage)` hooks.

### 9.2 Current lifecycle visibility

Under the current implementation:

* agents added after the initial candidate list is created do not participate in any stage of the current scheduler call;
* agents marked not alive during an earlier stage are skipped in later stages;
* current collection membership is not independently revalidated;
* each shuffled stage may have a different order;
* stage methods must exist and be callable.

### 9.3 Required documentation

A staged model must report:

* stage names and order;
* whether stage-level shuffling is enabled;
* which state changes are visible to later stages;
* whether removals may occur during stages;
* what model hooks do;
* which random stream controls stage order.

---

## 10. Agent creation and removal

### 10.1 Current creation behavior

An agent added after an activation snapshot is created is generally excluded from that existing snapshot.

The exact future eligibility point depends on whether the model uses:

* collection bulk operations;
* sequential activation;
* random activation;
* simultaneous activation;
* staged activation;
* custom iteration.

### 10.2 Current removal behavior

`Model.remove_agent(...)` coordinates removal from the model collection, world, lifecycle state, and owned-event cancellation according to the current lifecycle implementation.

Direct collection removal has a narrower responsibility and must not automatically be assumed to perform the complete model-level lifecycle operation.

### 10.3 Target lifecycle contract

The target lifecycle contract is:

```text
create during activation
→ registered immediately
→ not activated until the next activation pass

remove during activation
→ marked ineligible immediately
→ no later callback in the same pass
→ removed from all registered spaces
→ owned-event policy applied
→ lifecycle record emitted once
```

The target contract will also define:

* identifier reuse policy;
* idempotent or error behavior for repeated removal;
* model–collection–space referential-integrity checks;
* event-owner behavior;
* persistent identity fields for recorded data.

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

| Topic                     | Current guarantee                                        | Not currently guaranteed                                    |
| ------------------------- | -------------------------------------------------------- | ----------------------------------------------------------- |
| Fixed-step time           | `steps += 1`, `time += 1.0` after a completed model step | Variable or continuous time                                 |
| Events                    | Due events processed before `model.step()`               | Exact fractional-time execution                             |
| Event ordering            | Time, priority, sequence, event id                       | Context-independent same-time semantics                     |
| Collection `do()`         | Initial insertion-order snapshot                         | Removal-aware eligibility                                   |
| Collection `shuffle_do()` | Seeded permutation of initial snapshot                   | Removal-aware eligibility or independent RNG stream         |
| Sequential activation     | Initial order with `is_alive` checks                     | Membership revalidation                                     |
| Random activation         | Initial alive list, seeded permutation                   | Independence from behavior RNG draws                        |
| Simultaneous activation   | All `step()` calls before `advance()` calls              | State isolation or mandatory `advance()`                    |
| Staged activation         | Declared stage order and optional per-stage shuffle      | Dynamic additions within current scheduler call             |
| Recording                 | Post-step records with incremented counters              | Automatic time-zero observation                             |
| Scenario stop             | Pre-step and post-step callback checks                   | Automatic scientific analysis eligibility                   |
| Failure                   | Failed status and raised exception                       | Step rollback                                               |
| Snapshot                  | Selected model, agent, and RNG state                     | Full world, scheduler, event callback, and recorder restore |
| Reproducibility           | Conditional same-seed rerun                              | Cross-platform or cross-version equality                    |

---

## 16. Public-alpha semantic blockers

The following issues must be resolved before the fixed-step execution profile can be treated as public-alpha semantics:

1. Collection bulk operations may invoke agents removed earlier in the same pass.
2. Fractional event times are accepted without exact fractional-time execution.
3. Valid stopped runs may be excluded from default analysis reports.
4. Simultaneous activation does not require a complete two-phase agent contract.
5. Scheduler randomness and agent behavior share one RNG stream.
6. Agent–collection–space lifecycle invariants are not uniformly enforced.
7. Canonical models lack sufficient scientific invariant and metamorphic tests.

These are correctness and scientific-interpretation issues, not cosmetic API preferences.

---

## 17. Model-author responsibilities

Until the target contracts are implemented, model authors should:

1. document the scheduler and activation order;
2. avoid direct dynamic removal inside `AgentCollection.do()` and `shuffle_do()`;
3. use integer event times in the fixed-step profile;
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

> A fixed-step Python ABM execution profile with pre-step event draining, user-defined model activation, post-step observation, multiple activation strategies, and provisional lifecycle and randomness semantics.

The target public-alpha contract is:

> A fixed-step execution profile with versioned phases, removal-aware agent eligibility, integer event ticks, explicit observation timing, strict two-phase simultaneous activation, and documented random-stream ownership.

Until the target blockers are resolved, researchers must state the exact ABMForge commit and the model-specific semantic assumptions used in their study.
