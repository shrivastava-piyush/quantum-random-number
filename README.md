# qrng — Quantum Random Number Generator

A production-grade Quantum RNG package optimized for classical simulation,
with a provider/consumer architecture and a hybrid-execution interface so
it can transparently target real QPU hardware later.

## Features

- **Backend:** `qiskit_aer.AerSimulator`, auto-detects GPU, falls back to
  high-precision CPU simulation.
- **Architecture:** Provider/Consumer split — `EntropyProvider` runs the
  circuit, `EntropyProcessor` runs post-processing.
- **Circuit:** parallel Hadamard + measurement register of configurable width.
- **Hybrid execution:** `HardwareInterface` ABC with a `SimulatedBackend`
  implementation and an `IBMQBackend` placeholder for future QPU support.
- **Post-processing:** Von Neumann decorrelation + Toeplitz-hash extractor.
- **Verification:** NIST SP 800-22 Frequency (Monobit), Shannon entropy
  (target H ≥ 0.99), throughput / latency benchmark.
- **Engineering:** `pydantic` configuration models, `logging` telemetry
  (stderr — stdout stays clean for piping).
- **CLI:** `click`-based, supports stdout piping to Unix tools.

## Install

```bash
pip install -e .
# optional extras
pip install -e '.[gpu]'    # enables qiskit-aer-gpu
pip install -e '.[ibmq]'   # enables qiskit-ibm-runtime for the placeholder
pip install -e '.[dev]'    # dev tooling
```

## Library usage

```python
from qrng import QRNGConfig, generate_bits

bits = generate_bits(256, config=QRNGConfig())
print(bits)
```

Or with explicit provider/consumer wiring:

```python
from qrng import QuantumEntropySource, EntropyProvider, EntropyProcessor

source = QuantumEntropySource()
provider = EntropyProvider(source)
processor = EntropyProcessor()

raw = provider.produce(1024, oversample=12.0)
processed = processor.process(raw.bits, target_bits=1024)
print(processed.bits[:64])
```

## CLI

```bash
# Pipe into a Unix tool:
qrng generate --bits 256 --format binary | shasum -a 256
qrng generate --bits 128 --format hex
qrng generate --bits 64                      # ASCII 0/1

# Run NIST monobit + Shannon entropy:
qrng verify --bits 4096 --output json

# Throughput benchmark:
qrng benchmark --bits 4096
```

All telemetry is emitted on stderr so stdout is safe to pipe.

## Project layout

```
quantum-random-number/
├── pyproject.toml
├── README.md
├── src/qrng/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── facade.py
│   ├── logging_utils.py
│   ├── backends/
│   │   ├── base.py           # HardwareInterface (ABC)
│   │   ├── simulated.py      # AerSimulator-backed
│   │   └── ibmq.py           # QPU placeholder
│   ├── core/
│   │   ├── entropy_source.py # Hadamard register
│   │   ├── provider.py       # Producer
│   │   └── processor.py      # Consumer / post-processing driver
│   ├── postprocess/
│   │   ├── von_neumann.py
│   │   └── toeplitz.py
│   └── verification/
│       ├── nist.py
│       ├── entropy.py
│       └── benchmark.py
└── tests/
```

## License

MIT — see `LICENSE`.
