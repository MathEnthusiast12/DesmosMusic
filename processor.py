import matplotlib.pyplot as plt
import pretty_midi
import math

bpm = 166*(1/60)
sampleJumpLength = 1/bpm * 1/8

def process(file):
    l = []

    midi_data = pretty_midi.PrettyMIDI(file)
    duration = midi_data.get_end_time()
    print("duration:", duration)
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            l.append([note.pitch, float(note.start), float(note.end), note.velocity])

    notes = []
    print(len(l))
    i = 0
    while i < duration:
        print(i)
        temp = []
        for val in l:
            if val[1] <= i and val[2] >= i:
                temp.append([round(400*math.pow(2, (val[0]-60)/12)), val[3]])
        notes.append(temp)

        i += sampleJumpLength

    listSet = []
    for j, val in enumerate(notes):
        if len(listSet) < len(val):
            listSet.append([])

        for ind, li in enumerate(listSet):
            while len(li) < j - 1:
                listSet[ind].append([0, 0])
            
            if ind < len(val):
                listSet[ind].append(val[ind])

    print(len(listSet), 214/sampleJumpLength, "\n")

    with open("velocity.txt", "w") as v:
        with open("song.txt", "w") as text:
            indexLi = []
            velLi = []
            for n, li in enumerate(listSet):
                indexLi.append("l_{" + str(n) + "}[i]")
                velLi.append("L_{" + str(n) + "}[i]")
                text.write("l_{" + str(n) + "} = " + str([item[0] for item in li]) + "\n")
                velMax = max([item[1] for item in li])
                v.write("L_{" + str(n) + "} = " + str([item[1]/velMax for item in li]) + "\n")

            print(indexLi)
            print(velLi)

if __name__ == "__main__":
    process("Sinner_s Finale.wav.mid")