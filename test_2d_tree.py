from _2d_tree import node, _2d_tree

if __name__ == "__main__":
    points = [
        node(1, 10.0, 20.0),
        node(2, 15.0, 25.0),
        node(3, 5.0, 30.0),
        node(4, 7.0, 10.0),
        node(5, 12.0, 15.0),
    ]

    tree = _2d_tree()
    tree.build(points)

    #search range: lat from 6 to 16, lon from 10 to 26
    results = tree.range_search((6, 16, 14, 26))
    for r in results:
        print(r)