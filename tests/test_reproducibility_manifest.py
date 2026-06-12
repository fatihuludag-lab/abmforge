import json

from abmforge import Model, Scenario


class EmptyModel(Model):
    def setup(self) -> None:
        self.record.metric("steps", lambda model: model.steps)

    def step(self) -> None:
        pass


def test_dataset_write_manifest_creates_json_file(tmp_path):
    scenario = Scenario(
        model=EmptyModel,
        seed=42,
        steps=2,
        parameters={"alpha": 0.1},
        name="manifest-test",
    )

    result = scenario.run()
    manifest_path = result.dataset.write_manifest(tmp_path)

    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["run_id"] == result.run_id
    assert manifest["n_model_records"] == 2
    assert manifest["runs"][0]["seed"] == 42
    assert manifest["runs"][0]["parameters"] == {"alpha": 0.1}
    assert manifest["runs"][0]["scenario"] == "manifest-test"
    assert "python_version" in manifest["runs"][0]
    assert "platform" in manifest["runs"][0]
    assert "abmforge_version" in manifest["runs"][0]


def test_dataset_write_manifest_accepts_json_path(tmp_path):
    scenario = Scenario(model=EmptyModel, seed=1, steps=1)
    result = scenario.run()

    manifest_path = result.dataset.write_manifest(tmp_path / "custom_manifest.json")

    assert manifest_path.name == "custom_manifest.json"
    assert manifest_path.exists()
