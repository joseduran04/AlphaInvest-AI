from __future__ import annotations

import platform
import sys

import torch
import transformers


def main() -> None:
    cuda_available = (
        torch.cuda.is_available()
    )

    print(
        "=" * 72
    )

    print(
        "ALPHAINVEST AI — "
        "TRANSFORMER ENVIRONMENT"
    )

    print(
        "=" * 72
    )

    print(
        "Python:",
        sys.version.split()[0],
    )

    print(
        "Platform:",
        platform.platform(),
    )

    print(
        "PyTorch:",
        torch.__version__,
    )

    print(
        "Transformers:",
        transformers.__version__,
    )

    print()

    print(
        "CUDA available:",
        cuda_available,
    )

    if cuda_available:
        print(
            "CUDA version:",
            torch.version.cuda,
        )

        print(
            "GPU count:",
            torch.cuda.device_count(),
        )

        print(
            "GPU:",
            torch.cuda.get_device_name(
                0
            ),
        )

        properties = (
            torch.cuda
            .get_device_properties(0)
        )

        memory_gb = (
            properties.total_memory
            / 1024**3
        )

        print(
            "GPU memory GB:",
            f"{memory_gb:.2f}",
        )

        device = "cuda"

    else:
        device = "cpu"

    print()

    print(
        "Selected device:",
        device,
    )

    print(
        "=" * 72
    )


if __name__ == "__main__":
    main()