from future.moves.itertools import zip_longest
import random
import itertools


class IntroductionPointSet(object):
    """
    A set of introduction points to included in a HS descriptor.

    Provided with a list of available introduction points for each backend
    instance for an onionbalance service. This object will store the set of
    available introduction points and allow IPs to be selected from the
    available set.

    This class tracks which introduction points have already been provided
    and tries to provide the most diverse set of IPs.
    """

    def __init__(self, intro_points):
        """
        'intro_points' is a list of lists that looks like this:
        [
          [<intro#1 of Instance#1, intro#2 of Instance#1...>],
          [<intro#1 of Instance#2, intro#2 of Instance#2...>],
          [<intro#1 of Instance#3, intro#2 of Instance#3...>],
          ...
        ]
        """
        # Shuffle the introduction point order before selecting IPs.
        # Randomizing now allows later calls to .choose() to be
        # deterministic.
        for instance_intro_points in intro_points:
            random.shuffle(instance_intro_points)
        random.shuffle(intro_points)

        self.intro_points = intro_points
        self._intro_point_generator = self._get_intro_point()

    def __len__(self):
        """Provide the total number of available introduction points"""
        return sum(len(ips) for ips in self.intro_points)

    def _get_intro_point(self):
        """
        [Private function]

        Generator function which yields an introduction point

        Iterates through all available introduction points and try
        to pick IPs breath first across all backend instances. The
        intro point set is wrapped in `itertools.cycle` and will provided
        an infinite series of introduction points.
        """

        # Combine intro points from across the backend instances and flatten
        intro_points = zip_longest(*self.intro_points)
        flat_intro_points = itertools.chain.from_iterable(intro_points)
        for intro_point in itertools.cycle(flat_intro_points):
            if intro_point:
                yield intro_point

    def choose(self, count=10, shuffle=True):
        """
        [Public API]

        Retrieve N introduction points from the set of IPs

        Where more than `count` IPs are available, introduction points are
        selected to try and achieve the greatest distribution of introduction
        points across all of the available backend instances.

        Return a list of IntroductionPoints.
        """

        # Limit `count` to the available number of IPs to avoid repeats.
        count = min(len(self), count)
        choosen_ips = list(itertools.islice(self._intro_point_generator, count))

        if shuffle:
            random.shuffle(choosen_ips)
        return choosen_ips
