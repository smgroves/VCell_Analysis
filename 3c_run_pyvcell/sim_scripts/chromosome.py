import pandas as pd
import numpy as np

def metaphase_chromosomes():
    # chromosome length in metaphase #check where these are coming from
    chromosome_dict = {
        "chr1": [7.544134, 0.04106778919],
        "chr2": [7.339197848, 0.03995218405],
        "chr3": [6.008956333, 0.03271078588],
        "chr4": [5.764077424, 0.03137774548],
        "chr5": [5.501159364, 0.02994650586],
        "chr6": [5.175938758, 0.02817611163],
        "chr7": [4.828665848, 0.0262856719],
        "chr8": [4.398140485, 0.02394203314],
        "chr9": [4.193779303, 0.02282955795],
        "chr10": [4.054467333, 0.02207118931],
        "chr11": [4.093534, 0.02228385542],
        "chr12": [4.038645727, 0.02198506168],
        "chr13": [3.465585697, 0.01886551098],
        "chr14": [3.24374903, 0.01765790498],
        "chr15": [3.090642091, 0.01682444106],
        "chr16": [2.737525606, 0.01490219083],
        "chr17": [2.522952758, 0.01373412667],
        "chr18": [2.435554091, 0.01325835702],
        "chr19": [1.776291394, 0.009669547294],
        "chr20": [1.952853545, 0.01063069369],
        "chr21": [1.41545403, 0.007705267128],
        "chr22": [1.539953576, 0.008383001788],
        "chrX": [4.72851197, 0.02574046706],
        "chrY": [1.734164091, 0.01490219083]
    }
    return chromosome_dict


def calculate_pmp_length_df(metaphase_chromosome_dict: dict) -> pd.DataFrame:
    nucleosome_conc = {
        "PMP1": 400,
        "PMP2": 510,
        "PMP3": 590,
        "PMP4": 708.6,
        "Metaphase": 760
    }

    pmp_lengths = pd.DataFrame(index=metaphase_chromosome_dict.keys(),
                               columns=nucleosome_conc.keys())
    pmp_lengths["Metaphase"] = [metaphase_chromosome_dict[chr][0] for chr in pmp_lengths.index]
    for chr in pmp_lengths.index:
        for pmp_key in pmp_lengths.columns:
            pmp_lengths.loc[chr, pmp_key] = pmp_lengths.loc[chr, "Metaphase"] * (
                nucleosome_conc["Metaphase"] / nucleosome_conc[pmp_key])

    return pmp_lengths


def calculate_scaling_factor_df(pmp_lengths: pd.DataFrame) -> pd.DataFrame:
    # (chr_L over sum of chr_L) /2
    scaling_factor_df = pmp_lengths.div(pmp_lengths.sum(axis=0), axis=1)/2
    return scaling_factor_df

