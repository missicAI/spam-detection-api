import json

from spamguard.training import train

if __name__ == "__main__":
    report = train()
    print(
        json.dumps(
            {
                "cleaning": report["cleaning"],
                "split": report["split"],
                "metrics": report["metrics"],
                "baseline": report["baseline"],
            },
            indent=2,
        )
    )
