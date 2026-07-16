class FinalDecision:

    def decide(self, results):

        confidence = results.get("Confidence Engine", 0)

        nbs = results.get("NBS Engine", {})

        return {
            "confidence": confidence,
            "nbs": nbs
        }