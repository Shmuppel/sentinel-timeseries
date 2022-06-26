class Band:
    def __init__(
            self,
            name: int,
            path: str,
            spatial_resolution: int,
    ):
        self.name = name
        self.path = path
        self.spatial_resolution = spatial_resolution
        self.array = None
        self.array_affine_transform = None

    def __add__(self, other):
        return self.array + other.array

    def __sub__(self, other):
        return self.array - other.array

    def __mul__(self, other):
        return self.array * other.array
