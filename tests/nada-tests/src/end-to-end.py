from nada_dsl import *
from nada_ai.nn import Module, Conv2d, AvgPool2d, Linear, Flatten, ReLU
import nada_algebra as na


def nada_main():
    party = Party("party")

    x = na.array((1, 3, 4, 3), party, "input_x", na.SecretRational)

    class TestModuleConv(Module):
        def __init__(self) -> None:
            super(TestModuleConv, self).__init__()
            self.conv = Conv2d(kernel_size=2, in_channels=3, out_channels=2)
            self.pool = AvgPool2d(kernel_size=2)

        def forward(self, x: na.NadaArray) -> na.NadaArray:
            x = self.conv(x)
            x = self.pool(x)
            return x

    class TestModule(Module):
        def __init__(self) -> None:
            self.conv_module = TestModuleConv()
            self.flatten = Flatten(0)
            self.relu = ReLU()
            self.linear = Linear(2, 2)

        def forward(self, x: na.NadaArray) -> na.NadaArray:
            x = self.conv_module(x)
            x = self.flatten(x)
            x = self.linear(x)
            x = self.relu(x)
            return x

    module = TestModule()

    module.load_state_from_network("testmod", party)

    result = module(x)

    assert result.shape == (2,), result.shape

    return result.output(party, "output")
