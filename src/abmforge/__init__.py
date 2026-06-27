# ruff: noqa: F401
"""ABMForge public API.

The top-level imports in this module are the package's alpha-stage public import
surface. The authoritative list and stability grouping live in
``abmforge.api`` so accidental public API changes are caught by tests.
"""

from abmforge._version import __version__
from abmforge.analysis import (
    SALibProblem,
    SensitivityAnalysis,
    analyze_morris,
    analyze_sobol,
    sample_morris,
    sample_sobol,
)
from abmforge.api import PUBLIC_API
from abmforge.core.agent import Agent
from abmforge.core.collection import AgentCollection
from abmforge.core.model import Model
from abmforge.data import (
    DATASET_SCHEMA_VERSION,
    Dataset,
    DatasetSchemaV1,
    Recorder,
    SchemaValidationError,
)
from abmforge.experiment.archive import ExperimentArchive
from abmforge.experiment.experiment import Experiment, ExperimentResult
from abmforge.experiment.parameter_grid import ParameterGrid
from abmforge.experiment.registry import ExperimentRegistry
from abmforge.experiment.result import RunResult
from abmforge.experiment.scenario import Scenario
from abmforge.methods import ODDDocument
from abmforge.replay.snapshot import (
    attach_snapshot_hash,
    link_snapshot,
    read_snapshot,
    snapshot_hash,
    write_snapshot,
)
from abmforge.replay.validation import ReplayValidationReport, validate_replay
from abmforge.repro import ReproducibilityManifest
from abmforge.scheduling import (
    RandomActivation,
    Scheduler,
    SequentialActivation,
    SimultaneousActivation,
    StagedActivation,
)
from abmforge.time.event import Event
from abmforge.time.queue import EventQueue
from abmforge.visualization import plot_grid, plot_multiple_runs, plot_timeseries
from abmforge.world.continuous import ContinuousSpace
from abmforge.world.gis import GISSpace
from abmforge.world.grid import GridWorld
from abmforge.world.network import NetworkSpace

__all__ = list(PUBLIC_API)
