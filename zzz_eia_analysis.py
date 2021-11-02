import os
import pandas as pd

DESCRIPTION = 'description'
CLEAN_DESCRIPTION = 'clean description'

if __name__ == '__main__':
    filepath = r'C:\Users\PNorton\OneDrive - Hartree Partners\Documents\jira\doe mapping'
    filename = r'eia_weekly_202110071437'
    filetype = r'.xlsx'

    remove_prepositions = ['of', 'and', 'with', 'than', 'to', 'at', 'by', 'in', 'from']
    remove_non_product_words = ['imports', 'export', 'production', 'stocks', 'total', 'capacity', 'supply', 'ending', 'net', 'input']
    remove_countries = ['angola', 'brazil', 'ecuador', 'russia', 'equatorial', 'guinea', 'iraq', 'kuwait', 'mexico',
                        'nigeria', 'norway', 'saudi', 'canada', 'arabia', 'venezuela',
                        'algeria', 'congo', 'colombia']
    remove_countries.sort()

    remove_chars = [',']

    product_join_words = ['greater than 15 to 500 ppm sulfur',
                  'greater than 500 to 2000 ppm sulfur',
                  'greater than 2000 ppm sulfur',
                  'greater than 500 ppm sulfur',
                  '0 to 15 ppm sulfur',
                  'greater than 500 ppm sulfur',
                  'ed55 and lower',
                  'greater than ed55',
                  'fuel ethanol', 'fuel alcohol',
                  'motor gasoline',
                  'finished motor gasoline',
                  'finished conventional motor gasoline',
                  'finished conventional motor gasoline with ethanol',
                  'finished reformulated motor gasoline',
                  'finished reformulated motor gasoline with ethanol',
                  'gasoline blending components',
                  'reformulated motor gasoline',
                  'reformulated rbob',
                  'conventional other gasoline blending components',
                  'conventional cbob gasoline blending components',
                  'conventional gtab gasoline blending components',
                  'conventional motor gasoline',
                  'fuel oil', 'kerosene-type jet fuel',
                  'crude oil']
    other_join_words = ['excluding spr', 'united kingdom']
    join_words = product_join_words + other_join_words

    # longest are strongest; search longest keys first
    join_words.sort(key=len)
    join_words.reverse()

    remove_join_words = ['excluding_spr', 'united_kingdom']
    remove_words = remove_prepositions + remove_non_product_words + remove_countries + remove_join_words

    # load the xls
    file = os.path.join(filepath, filename + filetype)
    raw_df = pd.read_excel(file)

    # standardise the label and the content
    raw_df[DESCRIPTION] = raw_df['Description'].str.lower()
    raw_df.drop('Description', axis='columns')

    df_analysis = raw_df.copy(deep=True)

    # replace a specified sequence of words with a string joined by underscores
    df_analysis[CLEAN_DESCRIPTION] = df_analysis[DESCRIPTION]
    for index, row in df_analysis.iterrows():
        for j in join_words:
            row[CLEAN_DESCRIPTION] = row[CLEAN_DESCRIPTION].replace(j, '_'.join(j.split(' ')))

    # bucket of words
    one_giant_string = ' '.join(list(df_analysis[CLEAN_DESCRIPTION].values))
    words = one_giant_string.split(' ')
    # clean words
    words = [w.replace(char, '') for char in remove_chars for w in words]
    words = [w for w in words if w not in remove_words]

    # histogram of bucket of words
    data = {w: words.count(w) for w in words}
    df_word_count = pd.DataFrame.from_dict(data, orient='index')
    df_word_count.columns = ['count']
    df_word_count.sort_values('count', inplace=True, ascending=False)

    # ordered list of frequencies
    search_words = list(df_word_count.index)

    # add each word as a column and count its frequency in the bucket
    df = pd.DataFrame()
    for search in search_words:
        pattern = f'\\b({search})\\b'  # dont want to match gasoline in motor_gasoline
        df = df_analysis[CLEAN_DESCRIPTION].str.contains(pattern)
        df.name = search
        df_analysis = pd.concat([df_analysis, df], axis='columns')
    # turn boolean into integer values so we can sum them
    df_analysis[search_words] = df_analysis[search_words].applymap(lambda x: int(x))

    # create a proxy score for information content
    binary_values = [2 ** p for p in range(len(search_words), 0, -1)]
    df_analysis['score'] = df_analysis[search_words].dot(binary_values)
    df_analysis.sort_values('score', ascending=False, inplace=True)

    columns = list(raw_df.columns) + [CLEAN_DESCRIPTION, 'score']

    print(df_word_count.head(50))
    df_analysis.to_clipboard()

    # ax = df_analysis[search_words].plot.bar(stacked=True)
    # plt.show()

    print('hello')

    pass