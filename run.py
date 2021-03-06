#TODO: add randomized sampling

from model import *
from data_api import *

#1.3 mln przykladow na minute (u mnie 600k przykladow ok.)

def train_model():
    X = prepare_experiment_data(dataset="Wordnet", CV=0)

    networks = None

    if len(sys.argv) > 1:
        params = cPickle.load(open(sys.argv[1], "r"))
        R = range(11)
        networks = createNetworks(entity_matrix=X["E"], embedding_matrix=params["embedding_matrix"])
        pars = params["network_params"]
        for i, n in enumerate(networks):
            n.load_params(pars[i])
    else:
        networks = createNetworks(X["E"], X["U"], R=range(11), k=3)


    def compileAdaDelta(networks):
        trainers = []
        for n in networks:
            print("Creating trainer")
            trainers.append(AdaDelta(n,  lr=1e-5, num_updates=200, valid_freq=1))
        return trainers, networks

    def compileSGD(networks):
        trainers = []
        for n in networks:
            print("Creating trainer")
            trainers.append(SGD(n,  lr=6.0, num_updates=200, valid_freq=1))
        return trainers, networks

    def compileScipy(networks):
        trainers = []
        for n in networks:
            print("Creating trainer")
            trainers.append(Scipy(n, method='l-bfgs-b')) #L2=0))
        return trainers, networks

    trainers, networks = compileAdaDelta(networks)

    X_test = split_per_relation(X["X_test"], range(11))

    for i in range(1200):
        print("EPOCH"+str(i))
        batches_train = generate_batches(E=X, batch_size=40000, seed=i, both_sides=False)
        for batch_id, batch in enumerate(batches_train):
            print("-------------- "+str(batch[0,1])+" -----------")
            for k in range(1): #Just try overlearn 0 batch?
                costs = trainers[batch[0,1]].train_minibatch(batch)
                if len(costs):
                    cost_desc = ' '.join(
                    '%s=%.6f' % el for el in zip(trainers[0].cost_names, costs))
                    print(cost_desc)

        networks[0].update_EU()
        partial_results = [trainers[x[0,1]].f_eval(x) for x in X_test]
        print(partial_results)
        results_test = np.sum(partial_results, axis=0).reshape(-1)
        results_test[0:-1] = results_test[0:-1]/(float(results_test.shape[0]-1))

        print(results_test[-1])

        results_test[-1] = results_test[-1] / (float(X["X_test"].shape[0]))



        costs = list(zip(
            trainers[0].cost_names, #We can take any of those
            results_test))

        print(costs)

        if(i%50 == 0):
            saveNetworks(networks, "19_11_1"+str(i)+".cpickle")


train_model()
