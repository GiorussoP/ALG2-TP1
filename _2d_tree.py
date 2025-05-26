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
        if size == 0:
            return None
        if size == 1:
            return p_ord_lat[0]
        else:
            lat_left = []
            lat_right = []
            lon_left = []
            lon_right = []
            if depth % 2 != 0:
                #vertical cut: latitude
                median = size // 2
                vertex = p_ord_lat[median]

                lat_left = p_ord_lat[:median]
                lat_right = p_ord_lat[median+1:]

                #splitting points based on the lat_median
                for point in p_ord_lon:
                    if point.lat < vertex.lat:
                        lon_left.append(point)
                    elif point.lat > vertex.lat:
                        lon_right.append(point)
                    elif point != vertex:
                        if len(lon_left) <= len(lon_right):
                            lon_left.append(point)
                        else:
                            lon_right.append(point)
            else:
                #horizontal cut: longitude
                median = size // 2
                vertex = p_ord_lon[median]

                lon_left = p_ord_lon[:median]
                lon_right = p_ord_lon[median+1:]

                #splitting points based on the lon_median
                for point in p_ord_lat:
                    if point.lon < vertex.lon:
                        lat_left.append(point)
                    elif point.lon > vertex.lon:
                        lat_right.append(point)
                    elif point != vertex:
                        if len(lat_left) <= len(lat_right):
                            lat_left.append(point)
                        else:
                            lat_right.append(point)
                
        vertex.left = (self.__build_tree__(lat_left, lon_left, depth + 1))
        vertex.right = (self.__build_tree__(lat_right, lon_right, depth + 1))
        return vertex
    
    def build(self, points):
        p_ord_lat = sorted(points, key=lambda points: points.lat)
        p_ord_lon = sorted(points, key=lambda points: points.lon)
        self.root = self.__build_tree__(p_ord_lat, p_ord_lon, 0)

    def range_search(self, R):
        #range being (lat_low, lat_upp, lon_low, lon_upp)
        results = []
        self.__search__(self.root, R, 0, results)
        return results

    def __search__(self, vertex, R, depth, results):
        if vertex is None:
            return

        if vertex.left is None and vertex.right is None:
            #vertex is a leaf
            if vertex.in_range(R):
                #vertex in range
                results.append(vertex)
            return

        if depth % 2 == 0:
            #splitting on latitude
            if vertex.in_range(R):
                results.append(vertex)
            
            #checking if lc or rc could intersect R
            if vertex.left and R[0] <= vertex.lat:
                self.__search__(vertex.left, R, depth + 1, results)
            if vertex.right and R[1] >= vertex.lat:
                self.__search__(vertex.right, R, depth + 1, results)
        else:
            #splitting on longitude
            if vertex.in_range(R):
                results.append(vertex)

            #checking if lc or rc could intersect R
            if vertex.left and R[2] <= vertex.lon:
                self.__search__(vertex.left, R, depth + 1, results)
            if vertex.right and R[3] >= vertex.lon:
                self.__search__(vertex.right, R, depth + 1, results)



        