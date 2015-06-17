__author__ = 'Coleman'

import random

class Species:
    def __init__(self):
        self.representative = None
        self.organisms = []
        self.topFitness = 0
        self.averageFitness = 0
        self.staleness = 0

    def inSpecies(self, genome):
        pass

    def adjustedFitness(self, genome):
        pass

    def calculateFitness(self):
        pass

    def cull(self):
        pass

    def breedChild(self):
        pass

    def calculateStaleness(self):
        pass

class Organism:
    def __init__(self, inputs, outputs, genome):
        if genome is None:
            self.genome = Genome(inputs, outputs)

        else:
            self.genome = genome

        self.network = Network(self.genome)
        self.age = 0
        self.fitness = 0
        self.adjustedFitness = 0

    def breed(self, organism):
        pass

    def calculateFitness(self):
        pass

class Genome:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.genes = []
        self.numNeurons = 0

    def copy(self):
        newGenome = Genome(self.inputs, self.outputs)
        newGenome.genes = [gene.copy() for gene in self.genes]
        newGenome.numNeurons = self.numNeurons

        return newGenome

    def disjoint(self, other):
        maxInnovation = max(self.genes[-1].innovation, other.genes[-1].innovation)
        excessLimit = min(self.genes[-1].innovation, other.genes[-1].innovation)
        geneInnovations = [False for i in range(maxInnovation)]
        otherInnovations = [False for i in range(maxInnovation)]
        for gene in self.genes:
            geneInnovations[gene.innovation] = True

        for gene in other.genes:
            otherInnovations[gene.innovation] = True

        disjoint = 0
        for i in range(excessLimit):
            if not(geneInnovations[i] and otherInnovations[i]):
                disjoint += 1

        return disjoint

    def excess(self, other):
        maxInnovation = max(self.genes[-1].innovation, other.genes[-1].innovation)
        excessLimit = min(self.genes[-1].innovation, other.genes[-1].innovation)

        return maxInnovation - excessLimit

    def weight(self, other):
        maxInnovation = max(self.genes[-1].innovation, other.genes[-1].innovation)
        excessLimit = min(self.genes[-1].innovation, other.genes[-1].innovation)
        geneInnovations = [False for i in range(maxInnovation)]
        otherInnovations = [False for i in range(maxInnovation)]
        for gene in self.genes:
            geneInnovations[gene.innovation] = True

        for gene in other.genes:
            otherInnovations[gene.innovation] = True

        difference = []
        for i in range(excessLimit):
            if geneInnovations[i] and otherInnovations[i]:
                difference.append(abs(self.genes[i].weight - other.genes[i].weight))

        return sum(difference) / len(difference)

    def distance(self, other):
        global c1, c2, c3
        numGenes = max(len(self.genes), len(other.genes))

        return ((c1 * self.excess(other)) / numGenes) + ((c2 * self.disjoint(other)) / numGenes) + (c3 * self.weight(other))

    def mutate(self):
        global biasChance, weightChance, nodeChance, connectionChance, disableChance, enableChance
        if random.random() < biasChance:
            self.linkMutate(True)

        if random.random() < weightChance:
            self.pointMutate()

        if random.random() < nodeChance:
            self.nodeMutate()

        if random.random() < connectionChance:
            self.linkMutate()

        if random.random() < disableChance:
            self.disableMutate()

        if random.random() < enableChance:
            self.enableMutate()

    def pointMutate(self):
        global perturbChance, weightChange
        gene = random.choice(self.genes)
        if random.random() < perturbChance:
            gene.weight += random.uniform(-1, 1) * weightChange

        else:
            gene.weight = random.uniform(-1, 1)

    def linkMutate(self, bias):
        input = random.choice(list(range(self.numNeurons)) + self.inputs)
        if bias:
            input = "bias"

        output = random.choice(list(range(self.numNeurons)) + self.outputs)
        gene = Gene(0, input, output)
        if not self.containsLink(gene):
            self.genes.append(gene)

        gene.innovation = newInnovation()

    def nodeMutate(self):
        gene = random.choice(self.genes)
        gene.enabled = False
        self.numNeurons += 1
        self.genes.append(Gene(newInnovation(), gene.input, self.numNeurons))
        self.genes[-1].weight = 1
        self.genes.append(Gene(newInnovation(), self.numNeurons, gene.output))
        self.genes[-1].weight = gene.weight

    def enableMutate(self):
        gene = random.choice(self.genes)
        gene.enabled = True

    def disableMutate(self):
        gene = random.choice(self.genes)
        gene.enabled = False

    def containsLink(self, otherGene):
        for gene in self.genes:
            if otherGene.input == gene.input and otherGene.output == gene.output:
                return True

        return False

    def crossover(self, other, useOther):
        maxInnovation = max(self.genes[-1].innovation, other.genes[-1].innovation)
        excessLimit = min(self.genes[-1].innovation, other.genes[-1].innovation)
        geneInnovations = [False for i in range(maxInnovation)]
        otherInnovations = [False for i in range(maxInnovation)]
        for gene in self.genes:
            geneInnovations[gene.innovation] = True

        for gene in other.genes:
            otherInnovations[gene.innovation] = True

        child = Genome(self.inputs, self.outputs)
        for i in range(excessLimit):
            if geneInnovations[i] and otherInnovations[i]:
                if random.random() < 0.5:
                    child.genes.append(self.genes[i].copy())

                else:
                    child.genes.append(self.genes[i].copy())

            elif geneInnovations[i] or otherInnovations[i]:
                if useOther:
                    child.genes.append(other.genes[i].copy())

                else:
                    child.genes.append(self.genes[i].copy())

        return child

class Gene:
    def __init__(self, innovation, input, output):
        self.age = 0
        self.input = input
        self.output = output
        self.weight = random.uniform(-1, 1)
        self.innovation = innovation
        self.enabled = True
        self.recurrent = False

    def copy(self):
        newGene = Gene(self.innovation, self.input, self.output)
        newGene.age = self.age + 1
        newGene.weight = self.weight
        newGene.enabled = self.enabled

        return newGene

class Network:
    def __init__(self, genome):
        global recurrent
        self.neurons = {}
        self.outputs = {}

        self.neurons["bias"] = Neuron(0)
        for input in genome.inputs:
            self.neurons[input] = Neuron(0)

        for gene in genome.genes:
            if gene.enabled:
                if gene.input not in list(self.neurons.keys()):
                    self.neurons[gene.input] = Neuron(0)

                if gene.output not in list(self.neurons.keys()):
                    self.neurons[gene.output] = Neuron(self.neurons[gene.input].timeStep + 1)

                if gene.input.timeStep > gene.output.timeStep and recurrent:
                    gene.recurrent = True
                    self.neurons[gene.output].inputs.append(gene)

                elif gene.input.timeStep == gene.output.timeStep:
                    gene.output.timeStep += 1
                    self.neurons[gene.output].inputs.append(gene)

        for output in genome.outputs:
            found = False
            for key in list(self.neurons.keys()):
                if key is output:
                    found = True

            if not found:
                self.neurons[output] = Neuron(0)

            self.outputs[output] = self.neurons[output]

    def eval(self, inputs):
        for name in list(inputs.keys()):
            self.neurons[name] = inputs[name]

        for key in (self.neurons.keys()):
            neuron = self.neurons[key]
            neuron.sigmoid()

        outputs = {}
        for key in (self.outputs.keys()):
            outputs[key] = self.outputs[key].value

        return outputs

class Neuron:
    def __init__(self, timeStep):
        self.value = 1
        self.lastValue = 1
        self.inputs = []
        self.timeStep = timeStep

    def sigmoid(self):
        global steepness
        self.lastValue = self.value
        values = []
        for gene in self.inputs:
            if gene.recurrent:
                values.append(gene.input.lastValue)

            else:
                values.append(gene.input.value)

        x = sum(values)
        self.value = 2 / (steepness ** x + 1) - 1
        self.inputs = []

currentInnovation = -1
def newInnovation():
    global currentInnovation
    currentInnovation += 1
    return currentInnovation


# for main file
def step():
    global population
    for organism in population:
        organism.age += 1

distanceThreshold = 0
weightChange = .1
c1 = 0
c2 = 0
c3 = 0
perturbLimit = 0
biasChance = 0
perturbChance = 0
weightChance = 0
nodeChance = 0
connectionChance = 0
disableChance = 0
enableChance = 0

steepness = 5
recurrent = False

population = []
species = []

def rankGlobally(organism):
    pass