# Security experiments

These scripts generate the numerical evidence required for the two security demonstrations. They attack only local processes and never send submitted text to another service.

## Detection evasion

```powershell
python -m backend.experiments.detection_evasion
```

The script first keeps only fixed examples that the original document model correctly labels AI. It creates four attack variants per eligible example, measures the undefended predictions, applies the submitted normaliser, and repeats the same measurements. The JSON summary and per-variant CSV are written to `backend/experiments/results/`.

The examples are a small, original security test set rather than evidence of model accuracy. The limited confusable mapping reduces common attacks but does not cover the complete Unicode confusables standard. Expanding it would increase the risk of changing legitimate multilingual writing.

## Denial of service

```powershell
python -m backend.experiments.dos_experiment --requests 20
```

The script starts two temporary localhost servers and sends simultaneous HTTP requests to the real prediction route. The baseline accepts unbounded inference work. Protected mode uses the production semaphore and short bounded queue, returning `503` for excess work. A 250 ms experiment-only delay makes model cost repeatable on different computers. Production refuses artificial delays and refuses disabled DoS protection unless explicit experiment mode is enabled.

The comparison represents application-level resource exhaustion on one computer, not a distributed denial-of-service test.
