class node:
    def __init__(self, ID, lat, lon):
        self.ID = ID
        self.lat = lat
        self.lon = lon
        self.left = None
        self.right = None

    def __repr__(self):
        return f"(ID={self.ID}, lat={self.lat}, lon={self.lon})"
    
    def in_range(self, R):
        return R[0] <= self.lat <= R[1] and R[2] <= self.lon <= R[3]

class _2d_tree:
    def __init__(self):
        self.root = None

    def __build_tree__(self, p_ord_lat, p_ord_lon, depth):
        size = len(p_ord_lat)
        if size == 0 or len(p_ord_lon) == 0:
            return None
        if size == 1:
            return p_ord_lat[0]

        lat_left = []
        lat_right = []
        lon_left = []
        lon_right = []

        if depth % 2 != 0:
            #corte vertical: latitude
            median = size // 2
            vertex = p_ord_lat[median]

            lat_left = p_ord_lat[:median]
            lat_right = p_ord_lat[median+1:]

            #pegar os IDs das listas esquerda/direita
            ids_left = set(p.ID for p in lat_left)
            ids_right = set(p.ID for p in lat_right)

            #manter consistência com p_ord_lon
            lon_left = [p for p in p_ord_lon if p.ID in ids_left]
            lon_right = [p for p in p_ord_lon if p.ID in ids_right]
        else:
            #corte horizontal: longitude
            median = size // 2
            vertex = p_ord_lon[median]

            lon_left = p_ord_lon[:median]
            lon_right = p_ord_lon[median+1:]

            #pegar os IDs das listas esquerda/direita
            ids_left = set(p.ID for p in lon_left)
            ids_right = set(p.ID for p in lon_right)

            #manter consistência com p_ord_lat
            lat_left = [p for p in p_ord_lat if p.ID in ids_left]
            lat_right = [p for p in p_ord_lat if p.ID in ids_right]

        vertex.left = self.__build_tree__(lat_left, lon_left, depth + 1)
        vertex.right = self.__build_tree__(lat_right, lon_right, depth + 1)
        return vertex

    def build(self, points):
        p_ord_lat = sorted(points, key=lambda p: p.lat)
        p_ord_lon = sorted(points, key=lambda p: p.lon)
        self.root = self.__build_tree__(p_ord_lat, p_ord_lon, 0)

    def range_search(self, R):
        #range -> (lat_low, lat_upp, lon_low, lon_upp)
        results = []
        self.__search__(self.root, R, 0, results)
        return results

    def __search__(self, vertex, R, depth, results):
        if vertex is None:
            return

        if vertex.in_range(R):
            results.append(vertex)

        if depth % 2 == 0:
            #divisão em longitude (corte horizontal)
            if vertex.left and R[2] <= vertex.lon:
                self.__search__(vertex.left, R, depth + 1, results)
            if vertex.right and R[3] >= vertex.lon:
                self.__search__(vertex.right, R, depth + 1, results)
        else:
            #divisão em latitude (corte vertical)
            if vertex.left and R[0] <= vertex.lat:
                self.__search__(vertex.left, R, depth + 1, results)
            if vertex.right and R[1] >= vertex.lat:
                self.__search__(vertex.right, R, depth + 1, results)

    
    def __len__(self):
        return self.__count_nodes__(self.root)

    def __count_nodes__(self, node):
        if node is None:
            return 0
        return 1 + self.__count_nodes__(node.left) + self.__count_nodes__(node.right)




        