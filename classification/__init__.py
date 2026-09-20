"""Text classification tools for AI-generated content detection."""


def predict_text(*args, **kwargs):
    """Load the prediction function lazily to keep module execution clean."""
    from .predict import predict_text as _predict_text

    return _predict_text(*args, **kwargs)


__all__ = ["predict_text"]
