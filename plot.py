from dcodex.models import *
from .models import *

def plot_affiliation_matrix(
            family, 
            manuscripts, 
            verses,
            force_compute=False,
            matrix_filename=None,
            figsize=(12, 7),
            major_chapter_markers=10,
            minor_chapter_markers=1,
            labels=None,
            output_filename=None,
            colors=['#007AFF'],
            ):
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.ticker import FixedLocator
    from os.path import isfile
    from os import access, R_OK

    if not force_compute and matrix_filename and isfile( matrix_filename ) and access(matrix_filename, R_OK):
        matrix = np.load(matrix_filename)
    else:    
        matrix = family.affiliation_matrix( manuscripts, verses )
        if matrix_filename:
            np.save(matrix_filename, matrix)

    print(matrix)

    fig, ax = plt.subplots(figsize=figsize)

    ###### Major Grid Lines ######
    verse_min = verses[0]
    verse_max = verses[-1]
    
    chapter_beginnings = BibleVerse.objects.filter( id__gt=verse_min.id, id__lt=verse_max.id, verse=1 )

    major_tick_locations = [0]    
    major_tick_annotations = [verse_min.reference_abbreviation().replace(" ","\n")]
    for chapter_beginning in chapter_beginnings:
        if chapter_beginning.chapter % major_chapter_markers == 0 or chapter_beginning.chapter == 1:
            major_tick_locations.append( chapter_beginning.id - verse_min.id )
            ref = "%d:%d" % (chapter_beginning.chapter, chapter_beginning.verse) if chapter_beginning.chapter > 1 else chapter_beginning.reference_abbreviation().replace(" ","\n")
            major_tick_annotations.append( ref )
    major_tick_locations.append( verse_max.id - verse_min.id )
    major_tick_annotations.append( verse_max.reference_abbreviation().replace(" ","\n") )
    plt.xticks(major_tick_locations, major_tick_annotations )
    
    linewidth = 2 if major_chapter_markers > minor_chapter_markers else 1
    ax.xaxis.grid(True, which='major', color='#666666', linestyle='-', alpha=0.4, linewidth=linewidth)
    
    ###### Minor Grid Lines ######
    minor_ticks = [x.id - verse_min.id for x in chapter_beginnings if x.id not in major_tick_locations and x.chapter % minor_chapter_markers == 0]
    ax.xaxis.set_minor_locator(FixedLocator(minor_ticks))
    ax.xaxis.grid(True, which='minor', color='#666666', linestyle='-', alpha=0.2, linewidth=1,)

    x_values = np.arange( len(verses) )
    alpha = 0.4
    for manuscript_index, manuscript in enumerate(manuscripts):    
        color = colors[manuscript_index % len(colors)]
        ax.fill_between(x_values, manuscript_index + alpha * matrix[manuscript_index], manuscript_index - alpha * matrix[manuscript_index], color=color)

    if labels is None:
        labels = [ms.short_name() for ms in manuscripts]

    plt.yticks(np.arange(len(manuscripts)), labels)

    plt.show()

    distinct_verses = matrix.any(axis=0).sum()
    proportion = distinct_verses/len(verses) * 100.0
    print(f"Distinct verses {distinct_verses} ({proportion}\%)" )
    
    if output_filename:
        fig.tight_layout()
        fig.savefig(output_filename) 
        print(f"Saved to {output_filename}")