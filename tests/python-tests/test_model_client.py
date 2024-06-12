"""Model client unit tests"""

import pytest
import torch
import numpy as np

import nada_algebra as na
from sklearn.linear_model import LinearRegression, LogisticRegression
from torch import nn
from nada_ai.client import ModelClient, TorchClient, SklearnClient
import py_nillion_client as nillion


class TestModelClient:

    def test_sklearn_1(self):
        lin_reg = LinearRegression(fit_intercept=True)

        # Exporting untrained model should not be possible
        with pytest.raises(AttributeError):
            SklearnClient(lin_reg)

        X = np.array([[1, 2, 3], [2, 3, 4]])
        y = np.array([0, 1])

        lin_reg_fit = lin_reg.fit(X, y)

        SklearnClient(lin_reg_fit)

    def test_sklearn_2(self):
        log_reg = LogisticRegression(fit_intercept=False)

        # Exporting untrained model should not be possible
        with pytest.raises(AttributeError):
            SklearnClient(log_reg)

        X = np.array([[1, 2, 3], [2, 3, 4]])
        y = np.array([0, 1])

        log_reg_fit = log_reg.fit(X, y)

        SklearnClient(log_reg_fit)

    def test_sklearn_3(self):
        log_reg = LogisticRegression(fit_intercept=False)

        X = np.array([[1, 2, 3], [2, 3, 4]])
        y = np.array([0, 1])

        log_reg_fit = log_reg.fit(X, y)

        model_client = SklearnClient(log_reg_fit)

        secrets = model_client.export_state_as_secrets("test_model", na.SecretRational)

        assert len(secrets.keys()) == 3

        assert "test_model_coef_0_0" in secrets.keys()
        assert "test_model_coef_0_1" in secrets.keys()
        assert "test_model_coef_0_2" in secrets.keys()

    def test_sklearn_4(self):
        log_reg = LogisticRegression(fit_intercept=False)

        X = np.array([[1, 2, 3], [2, 3, 4]])
        y = np.array([0, 1])

        log_reg_fit = log_reg.fit(X, y)

        model_client = SklearnClient(log_reg_fit)

        with pytest.raises(NotImplementedError):
            model_client.export_state_as_secrets("test_model", nillion.SecretInteger)

    def test_custom_client_1(self):
        class MyModelClient(ModelClient):
            def __init__(self) -> None:
                self.state_dict = {"some_value": [1, 2, 3]}

        model_client = MyModelClient()

        secrets = model_client.export_state_as_secrets("test_model", na.Rational)

        assert list(sorted(secrets.keys())) == [
            "test_model_some_value_0",
            "test_model_some_value_1",
            "test_model_some_value_2",
        ]

    def test_custom_client_2(self):
        class MyModelClient(ModelClient):
            def __init__(self) -> None:
                self.some_value = {"some_value": 1}

        # Invalid model client: no state_dict defined
        with pytest.raises(AttributeError):
            MyModelClient()

    def test_torch_1(self):
        class TestModule(nn.Module):
            def __init__(self) -> None:
                super(TestModule, self).__init__()
                self.linear_0 = nn.Linear(3, 2)
                self.linear_1 = nn.Linear(2, 2)

            def forward(self, x: torch.Tensor) -> torch.Tensor:
                x = self.linear_0(x)
                x = self.linear_1(x)
                return x

        mod = TestModule()

        TorchClient(mod)

    def test_torch_2(self):
        class TestModule(nn.Module):
            def __init__(self) -> None:
                super(TestModule, self).__init__()
                self.linear_0 = nn.Linear(3, 2)
                self.linear_1 = nn.Linear(2, 2)

            def forward(self, x: torch.Tensor) -> torch.Tensor:
                x = self.linear_0(x)
                x = self.linear_1(x)
                return x

        mod = TestModule()

        model_client = TorchClient(mod)

        secrets = model_client.export_state_as_secrets("test_model", na.SecretRational)

        assert len(secrets) == 14

        expected_layers = [
            "test_model_linear_0.weight_0_0",
            "test_model_linear_0.weight_0_1",
            "test_model_linear_0.weight_0_2",
            "test_model_linear_0.weight_1_0",
            "test_model_linear_0.weight_1_1",
            "test_model_linear_0.weight_1_2",
            "test_model_linear_0.bias_0",
            "test_model_linear_0.bias_1",
            "test_model_linear_1.weight_0_0",
            "test_model_linear_1.weight_0_1",
            "test_model_linear_1.weight_1_0",
            "test_model_linear_1.weight_1_1",
            "test_model_linear_1.bias_0",
            "test_model_linear_1.bias_1",
        ]

        for expected_layer in expected_layers:
            assert expected_layer in secrets.keys()

    def test_torch_3(self):
        class TestModule(nn.Module):
            def __init__(self) -> None:
                super(TestModule, self).__init__()
                self.conv = nn.Conv2d(1, 1, 1)
                self.attn = nn.MultiheadAttention(2, 2)
                self.layer_norm = nn.LayerNorm((2,))
                self.gelu = nn.GELU()

            def forward(self, x: torch.Tensor) -> torch.Tensor:
                return x

        mod = TestModule()

        model_client = TorchClient(mod)

        secrets = model_client.export_state_as_secrets("test_model", na.SecretRational)

        assert len(secrets) == 30

        expected_layers = [
            "test_model_conv.weight_0_0_0_0",
            "test_model_conv.bias_0",
            "test_model_attn.in_proj_weight_0_0",
            "test_model_attn.in_proj_weight_0_1",
            "test_model_attn.in_proj_weight_1_0",
            "test_model_attn.in_proj_weight_1_1",
            "test_model_attn.in_proj_weight_2_0",
            "test_model_attn.in_proj_weight_2_1",
            "test_model_attn.in_proj_weight_3_0",
            "test_model_attn.in_proj_weight_3_1",
            "test_model_attn.in_proj_weight_4_0",
            "test_model_attn.in_proj_weight_4_1",
            "test_model_attn.in_proj_weight_5_0",
            "test_model_attn.in_proj_weight_5_1",
            "test_model_attn.in_proj_bias_0",
            "test_model_attn.in_proj_bias_1",
            "test_model_attn.in_proj_bias_2",
            "test_model_attn.in_proj_bias_3",
            "test_model_attn.in_proj_bias_4",
            "test_model_attn.in_proj_bias_5",
            "test_model_attn.out_proj.weight_0_0",
            "test_model_attn.out_proj.weight_0_1",
            "test_model_attn.out_proj.weight_1_0",
            "test_model_attn.out_proj.weight_1_1",
            "test_model_attn.out_proj.bias_0",
            "test_model_attn.out_proj.bias_1",
            "test_model_layer_norm.weight_0",
            "test_model_layer_norm.weight_1",
            "test_model_layer_norm.bias_0",
            "test_model_layer_norm.bias_1",
        ]

        for expected_layer in expected_layers:
            assert expected_layer in secrets.keys()

    def test_torch_4(self):
        class TestModule(nn.Module):
            def __init__(self) -> None:
                super(TestModule, self).__init__()
                self.linear_0 = nn.Linear(3, 2)
                self.linear_1 = nn.Linear(2, 2)

            def forward(self, x: torch.Tensor) -> torch.Tensor:
                x = self.linear_0(x)
                x = self.linear_1(x)
                return x

        mod = TestModule()

        model_client = TorchClient(mod)

        secrets = model_client.export_state_as_secrets("test_model", na.SecretRational)

        assert len(secrets) == 14

        expected_layers = [
            "test_model_linear_0.weight_0_0",
            "test_model_linear_0.weight_0_1",
            "test_model_linear_0.weight_0_2",
            "test_model_linear_0.weight_1_0",
            "test_model_linear_0.weight_1_1",
            "test_model_linear_0.weight_1_2",
            "test_model_linear_0.bias_0",
            "test_model_linear_0.bias_1",
            "test_model_linear_1.weight_0_0",
            "test_model_linear_1.weight_0_1",
            "test_model_linear_1.weight_1_0",
            "test_model_linear_1.weight_1_1",
            "test_model_linear_1.bias_0",
            "test_model_linear_1.bias_1",
        ]

        for expected_layer in expected_layers:
            assert expected_layer in secrets.keys()
