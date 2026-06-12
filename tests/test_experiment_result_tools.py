from abmforge import Agent, Experiment, Model


class DummyAgent(Agent):
    def step(self) -> None:
        self.value += 1


class DummyModel(Model):
    def setup(self) -> None:
        self.agents.create(DummyAgent, n=1, value=0)
        self.record.metric("total", lambda model: model.agents.sum("value"))

    def step(self) -> None:
        self.agents.do("step")


def test_experiment_result_summary():
    experiment = Experiment(
        model=DummyModel,
        parameters={"a": [1, 2]},
        seeds=[10, 20],
        steps=2,
    )

    result = experiment.run()
    summary = result.summary()

    assert summary["run_count"] == 4
    assert summary["successful_count"] == 4
    assert summary["failed_count"] == 0
    assert summary["statuses"] == {"completed": 4}


def test_experiment_result_combines_model_records():
    experiment = Experiment(
        model=DummyModel,
        parameters={"a": [1, 2]},
        seeds=[10],
        steps=2,
    )

    result = experiment.run()
    records = result.model_records()

    assert len(records) == 4
    assert all(record["metric"] == "total" for record in records)


def test_experiment_result_write_csv(tmp_path):
    experiment = Experiment(
        model=DummyModel,
        parameters={"a": [1, 2]},
        seeds=[10],
        steps=2,
    )

    result = experiment.run()
    output_dir = result.write_csv(tmp_path)

    assert (output_dir / "runs.csv").exists()
    assert (output_dir / "model_records.csv").exists()
    assert (output_dir / "agent_records.csv").exists()
    assert "completed" in (output_dir / "runs.csv").read_text(encoding="utf-8")
