from dcodex.models import *
from .models import *


# plt.style.use('seaborn-darkgrid')
from dcodex.similarity import (
    LIKELY__UNLIKELY,
    HIGHLY_LIKELY__ELSE,
    HIGHLY_LIKELY__LIKELY__ELSE,
    SOLID,
)


def plot_rolling_average(
    manuscript,
    mss_sigla,
    range=None,
    output_filename=None,
    csv_filename=None,
    force_compute=False,
    gotoh_param=[
        6.6995597099885345,
        -0.9209875054657459,
        -5.097397327423096,
        -1.3005714416503906,
    ],  # From PairHMM of whole dataset
    weights=[
        0.07124444438506426,
        -0.2723489152810223,
        -0.634987796501936,
        -0.05103656566400282,
    ],  # From whole dataset
    figsize=(12, 7),
    colors=["#007AFF", "#6EC038", "darkred"],
    mode=LIKELY__UNLIKELY,
    major_chapter_markers=5,
    minor_chapter_markers=1,
    ymin=60,
    ymax=100,
    annotations=[],
    annotation_color="red",
    annotations_spaces_to_lines=False,
    legend_location="best",
):

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import rcParams

    rcParams["font.family"] = "Linux Libertine O"
    rcParams.update({"font.size": 14})
    import matplotlib.ticker as mtick
    import matplotlib.lines as mlines
    from os import access, R_OK
    from os.path import isfile

    from matplotlib.ticker import FixedLocator

    if not isinstance(manuscript, Manuscript):
        manuscript = Manuscript.find(manuscript)

    fig, ax = plt.subplots(figsize=figsize)

    mss = [Manuscript.find(siglum) for siglum in mss_sigla.keys()]

    if (
        not force_compute
        and csv_filename
        and isfile(csv_filename)
        and access(csv_filename, R_OK)
    ):
        df = pd.read_csv(csv_filename)
    else:
        transcriptions = manuscript.transcriptions_range(range=range)
        df = manuscript.rolling_average_probability(
            mss=mss,
            transcriptions=transcriptions,
            gotoh_param=gotoh_param,
            weights=weights,
            prior_log_odds=0.0,
        )
        if csv_filename:
            df.to_csv(csv_filename)

    df = df.set_index("verse__id")

    min = df.index.min()
    max = df.index.max()
    df = df.reindex(np.arange(min, max + 1))

    for index, ms_siglum in enumerate(mss_sigla.keys()):
        if mode is HIGHLY_LIKELY__LIKELY__ELSE:
            plt.plot(
                df.index,
                df[ms_siglum + "_similarity"].mask(
                    df[ms_siglum + "_probability"] < 0.95
                ),
                "-",
                color=colors[index],
                linewidth=2.5,
                label=mss_sigla[ms_siglum] + " (Highly Likely)",
            )
            plt.plot(
                df.index,
                df[ms_siglum + "_similarity"].mask(
                    (df[ms_siglum + "_probability"] > 0.95)
                    | (df[ms_siglum + "_probability"] < 0.5)
                ),
                "-",
                color=colors[index],
                linewidth=1.5,
                label=mss_sigla[ms_siglum] + " (Likely)",
            )
            plt.plot(
                df.index,
                df[ms_siglum + "_similarity"].mask(
                    df[ms_siglum + "_probability"] > 0.95
                ),
                "--",
                color=colors[index],
                linewidth=0.5,
                label=mss_sigla[ms_siglum] + " (Unlikely)",
            )

        elif mode is HIGHLY_LIKELY__ELSE:
            plt.plot(
                df.index,
                df[ms_siglum + "_similarity"].mask(
                    df[ms_siglum + "_probability"] < 0.95
                ),
                "-",
                color=colors[index],
                linewidth=2.5,
                label=mss_sigla[ms_siglum] + " (Highly Likely)",
            )
            plt.plot(
                df.index,
                df[ms_siglum + "_similarity"],
                "--",
                color=colors[index],
                linewidth=1,
                label=mss_sigla[ms_siglum],
            )
        else:
            plt.plot(
                df.index,
                df[ms_siglum + "_similarity"].mask(
                    df[ms_siglum + "_probability"] < 0.5
                ),
                "-",
                color=colors[index],
                linewidth=2.5,
                label=mss_sigla[ms_siglum] + " (Likely)",
            )
            plt.plot(
                df.index,
                df[ms_siglum + "_similarity"],
                "--",
                color=colors[index],
                linewidth=1,
                label=mss_sigla[ms_siglum] + " (Unlikely)",
            )
    #            plt.plot(df.index, df[ms_siglum+'_similarity'].mask(df[ms_siglum+"_probability"] > 0.5), '--', color=colors[index], linewidth=1, label=mss_sigla[ms_siglum] + " (Unlikely)" );

    plt.ylim([ymin, ymax])
    ax.set_xticklabels([])

    plt.ylabel("Similarity", horizontalalignment="right", y=1.0)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

    #######################
    ##### Grid lines  #####
    #######################

    verse_min = BibleVerse.objects.get(id=min)
    verse_max = BibleVerse.objects.get(id=max)

    chapter_beginnings = BibleVerse.objects.filter(id__gt=min, id__lt=max, verse=1)

    ###### Major Grid Lines ######
    major_tick_locations = [min]
    major_tick_annotations = [verse_min.reference_abbreviation().replace(" ", "\n")]
    for chapter_beginning in chapter_beginnings:
        if (
            chapter_beginning.chapter % major_chapter_markers == 0
            or chapter_beginning.chapter == 1
        ):
            major_tick_locations.append(chapter_beginning.id)
            ref = (
                "%d:%d" % (chapter_beginning.chapter, chapter_beginning.verse)
                if chapter_beginning.chapter > 1
                else chapter_beginning.reference_abbreviation().replace(" ", "\n")
            )
            major_tick_annotations.append(ref)
    major_tick_locations.append(verse_max.id)
    major_tick_annotations.append(verse_max.reference_abbreviation().replace(" ", "\n"))
    plt.xticks(major_tick_locations, major_tick_annotations)

    linewidth = 2 if major_chapter_markers > minor_chapter_markers else 1
    ax.xaxis.grid(
        True,
        which="major",
        color="#666666",
        linestyle="-",
        alpha=0.4,
        linewidth=linewidth,
    )

    ###### Minor Grid Lines ######
    minor_ticks = [
        x.id
        for x in chapter_beginnings
        if x.id not in major_tick_locations and x.chapter % minor_chapter_markers == 0
    ]
    ax.xaxis.set_minor_locator(FixedLocator(minor_ticks))
    ax.xaxis.grid(
        True,
        which="minor",
        color="#666666",
        linestyle="-",
        alpha=0.2,
        linewidth=1,
    )

    ###### Annotations ######
    for annotation in annotations:
        if type(annotation) == tuple:
            annotation_verse = annotation[0]
            annotation_description = annotation[-1]
        else:
            annotation_verse = annotation_description = annotation

        if annotations_spaces_to_lines:
            annotation_description = annotation_description.replace(" ", "\n")
        verse = BibleVerse.get_from_string(annotation_verse)
        plt.axvline(x=verse.id, color=annotation_color, linestyle="--")
        ax.annotate(
            annotation_description,
            xy=(verse.id, ymax),
            xycoords="data",
            ha="center",
            va="bottom",
            xytext=(0, 10),
            textcoords="offset points",
            fontsize=10,
            family="Linux Libertine O",
            color=annotation_color,
        )

    ax.legend(
        shadow=False,
        title="",
        framealpha=1,
        edgecolor="black",
        loc=legend_location,
        facecolor="white",
    )

    plt.show()

    if output_filename:
        fig.tight_layout()
        fig.savefig(output_filename)
