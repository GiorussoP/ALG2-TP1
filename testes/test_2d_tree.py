from _2d_tree import node, _2d_tree
from tree_csv_aux_functions import build_aux_structures, format_results

if __name__ == "__main__":

    print("Teste pequeno e artificial")

    points = [
    node("A", -23.550520, -46.633308),
    node("B", -23.550521, -46.633307),
    node("C", -23.550522, -46.633306),
    node("D", -23.550523, -46.633305),
    node("E", -23.550524, -46.633304)
    ]

    tree_artf = _2d_tree()
    tree_artf.build(points)
    search_range = (-23.550523, -23.550520, -46.633308, -46.633306)

    results = tree_artf.range_search(search_range)
    for node in results:
        print(node)

    print("\n\tTeste com dados completos\n")

    path = "./bares_restaurantes.csv"

    data_vector = []
    points = []
    points, data_vector = build_aux_structures(path)

    tree = _2d_tree()
    tree.build(points)

    print(tree.__len__())

    print("\n\ttestando para range sem elementos")
    result = tree.range_search((-19.911468,-19.909732, -43.954193, -43.951125))
    print(len(result))
    print(result)
    print(format_results(result, data_vector))

    print("\ttestando para um unico elemento ")
    result = tree.range_search((-19.959328, -19.959328, -44.001602, -44.001602))
    print(len(result))
    print(result)
    print(format_results(result, data_vector))

    print("\ttestando para um pequeno range")
    result = tree.range_search((-19.909574, -19.907233, -43.965182, -43.961234))
    print(len(result))
    print(result)
    print(format_results(result[:3], data_vector))

    print("\ttestando para range moderado")
    result = tree.range_search((-19.926894, -19.916077,-43.947619, -43.933285))
    print(len(result))
    print(result[:3])
    print(format_results(result[:3], data_vector))

    print("\ttestando para o maior range (todos os pontos)")
    result = tree.range_search((-20.069097,-19.765567 ,-44.211557, -43.702066))
    print(len(result))
    print(result[:3])
    print(format_results(result[:3], data_vector))


        