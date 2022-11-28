from django.test.runner import DiscoverRunner


class HinesTestRunner(DiscoverRunner):
    "To enable some settings for every test run."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only display a test's output if it fails.
        self.buffer = True

        # Run tests in random order.
        if self.shuffle is False:
            self.shuffle = None  # means “autogenerate a seed”
