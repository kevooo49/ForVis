import logging
import re


class SensitiveFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%',
                 sensitive_patterns=[]):
        super().__init__(fmt, datefmt, style)

        self.compiled_patterns = [
            re.compile(pattern)
            for pattern in sensitive_patterns
        ]

    def format(self, record):
        formatted = super().format(record)
        redacted_log = formatted
        for compiled_re in self.compiled_patterns:
            redacted_log = compiled_re.sub("(REDACTED)", redacted_log)
        return redacted_log






