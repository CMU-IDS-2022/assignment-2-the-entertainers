# important libraries
import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib

# Use the full page instead of a narrow central column
st.set_page_config(layout="wide")

# title of application
st.title("Recognizing Patterns in Songs")


# add caching so we load the data only once
@st.cache
def load_data():
    # Load song dataset
    csv_file = "features_30_sec.csv"
    return pd.read_csv(csv_file)

@st.cache
def playAudio(genre, playlist):
    # open and play the audio file
    audio_file = open('genres_original/' + genre_selection + '/' + song_selection, 'rb')
    audio_bytes = audio_file.read()
    return audio_bytes


# load dataset
df = load_data()

# introduction and instructions on application
st.info(
    "This application allows users to explore the question, “How can we categorize different songs based on their audio features? What patterns emerge?” Using the visualization, the user will be able to discover relationships and patterns among a song’s audio features, and how that is correlated to the song’s genre. ")

# default features for scatterplot

# multiselect to change features on X and Y axis for scatterplot (first choice is X and second choice is Y)
features = st.multiselect('Choose X and Y features to see how they correlate:',
                          ("harmony_mean", "rms_mean", "chroma_stft_mean", "rolloff_mean", "tempo"),
                          default=["tempo", "chroma_stft_mean"])
if len(features) < 2:
    feature_X = "tempo"
    feature_Y = "chroma_stft_mean"
else:
    feature_X = str(features[0])
    feature_Y = str(features[1])

# dividing the application into columns
col1, col2 = st.columns((2, 1))

# brush (click and drag) for selecting specific values on chart
brush = alt.selection_interval(encodings=["x"])

# selection to allow highlight of genre when click on legend
selection = alt.selection_multi(fields=['label'], bind='legend')

# scatterplot showing the correlation between two features for all genres
scatterplot = alt.Chart(df).mark_circle(size=100).encode(
    alt.X(feature_X, scale=alt.Scale(zero=False)),
    alt.Y(feature_Y, scale=alt.Scale(zero=False)),
    alt.Color('label:N', legend=alt.Legend(title="Genres")),
    opacity=alt.condition(selection, alt.value(1), alt.value(0))
    , tooltip=['filename', 'label', 'tempo', 'chroma_stft_mean']
).properties(
    width=650, height=350
).transform_filter(
    brush
).interactive().add_selection(
    selection
)

features_pie = df.label.unique() #list(set(feature_X + feature_Y))

nBlues = df[df.label == 'blues'].shape[0]
nClassical = df[df.label == 'classical'].shape[0]
nCountry = df[df.label == 'country'].shape[0]
nDisco = df[df.label == 'disco'].shape[0]
nHiphop = df[df.label == 'hiphop'].shape[0]
nJazz = df[df.label == 'jazz'].shape[0]
nMetal = df[df.label == 'metal'].shape[0]
nPop = df[df.label == 'pop'].shape[0]
nReggae = df[df.label == 'reggae'].shape[0]
nRock = df[df.label == 'rock'].shape[0]

value_list = [nBlues, nClassical,nCountry,nDisco,nHiphop,nJazz,nMetal,nPop,nReggae,nRock]
    
# facet charts that show grid of scatterplots for each genre
facet = alt.Chart(df).mark_point().encode(
    alt.X('tempo:Q'),
    alt.Y('chroma_stft_mean:Q'),
    alt.Color('label:N', legend=alt.Legend(title="Genres")), facet=alt.Facet('label:N', columns=5),
    tooltip=['filename', 'label', 'chroma_stft_mean', 'tempo']
).properties(
    width=110,
    height=110
).transform_filter(brush).interactive()

# set overview intiall to the scatterplot visualization
overview = scatterplot

# creating strip plot visualizations
# strip plot visualization for chroma_stft_mean
chart = alt.Chart(df).mark_tick().encode(
    x='chroma_stft_mean', color=alt.condition(brush, "label", alt.value("white"), legend=None),
    tooltip=['filename', 'label', 'chroma_stft_mean']
).properties(
    width=650, height=45
).add_selection(brush)

# strip plot visualization for rms_mean
chart2 = alt.Chart(df).mark_tick().encode(
    x='rms_mean', color=alt.condition(brush, "label", alt.value("white")),
    tooltip=['filename', 'label', 'rms_mean'],
).properties(
    width=650, height=45
).add_selection(brush)

# strip plot visualization for rolloff_mean
chart3 = alt.Chart(df).mark_tick().encode(
    x='rolloff_mean', color=alt.condition(brush, "label", alt.value("white")),
    tooltip=['filename', 'label', 'rolloff_mean']
).properties(
    width=650, height=45
).add_selection(brush)

# strip plot visualization for harmony_mean
chart4 = alt.Chart(df).mark_tick().encode(
    x='harmony_mean', color=alt.condition(brush, "label", alt.value("white")),
    tooltip=['filename', 'label', 'harmony_mean']
).properties(
    width=650, height=45
).add_selection(brush)

# strip plot visualization for tempo
chart5 = alt.Chart(df).mark_tick().encode(
    x='tempo', color=alt.condition(brush, "label", alt.value("white")),
    tooltip=['filename', 'label', 'tempo']
).properties(
    width=650, height=45
).add_selection(brush)

# elements that go into column 1 (scatterplot and strip plots)
with col1:
    st.subheader("Analyze the correlation among genres: ")

    # checkbox that changes the scatterplot to grid of scatterplots for eac genre
    if st.checkbox("Click for Genre Breakdown"):
        overview = facet

    # create the scatterplot and strip plot visualizations in a vertical orientation
    st.write(overview & chart & chart2 & chart3 & chart4 & chart5)

# elements that go into column 2 (songs selection, audio file, )
with col2:
    st.subheader("Explore the songs: ")

    # get list of genres from dataset
    genres = df.label.unique()
    genre_selection = st.selectbox("Pick a Genre", genres, 0)

    # get all the songs in the selected genre
    playlist = df[df['label'] == genre_selection].filename
    song_selection = st.selectbox("Pick a Song", playlist, 0)

    song = playAudio(genre_selection, song_selection)
    st.audio(song, format='audio/wav')

    # expander - when clicked, shows the written descriptions of the features
    with st.expander("See description of features", expanded=True):
        st.write("chroma_stft: represents information about the classification of pitch and signal structure, units = intensity")
        st.write("rms: a metering tool that measures the average loudness of an audio track within a window of roughly 300 milliseconds, units=intensity")
        st.write(
            "rolloff: denotes the approximate low bass and high treble limits in a frequency response curve, with all frequencies between being those a speaker will play accurately")
        st.write(
            "harmony: the process by which the composition of individual sounds, or superpositions of sounds, is analysed by hearing.")
        st.write("tempo: how fast or slow a piece of music is performed (units = beats per minute (BPM)")

    with st.expander("Genre breakdown pie chart"):
        st.subheader("Proportion of genres in the dataset:")
        st.subheader("#")
        st.subheader("#")

        # create pie chart
        fff, middlex = plt.subplots(nrows=1, ncols=1, figsize = (2,2))

        colors = ('b', 'darkorange','r', 'c', 'g', 'gold', 'm', 'hotpink', 'sienna', 'silver')

        middlex.pie(value_list, labels=features_pie, colors = colors, textprops={'fontsize': 6})
        st.pyplot(fff)
    
st.markdown("---")
st.markdown("#")
# dividing the application into columns
col3, col4 = st.columns((2, 1))

#intercorrelation heatmap

with col3:
    if True: #st.button('Intercorrelation Heatmap'):
        with col4:
            st.subheader("Intercorrelation heatmap:")
            sorted_unique_features = sorted({'chroma_stft_mean', 'rms_mean', 'tempo', 'rolloff_mean', 'harmony_mean'})
            selected_features = st.multiselect('Features to be included in heatmap:', sorted_unique_features, sorted_unique_features)

            # Sidebar - Position selection
            unique_genres = sorted(df.label.unique())
            selected_genres = st.multiselect('Features to be included in correlation calculation:', unique_genres, unique_genres)

            # Filtering data
            df_selected = df[df.label.isin(selected_genres)]
            df_selected = df_selected[selected_features]

        # Heatmap
        corr = df_selected.corr()
        mask = np.zeros_like(corr)
        mask[np.triu_indices_from(mask, k=1)] = True
        if st.checkbox("Scale from minimum value ro maximum value"):
            vmin = corr.min().min()
            vmax = corr.max().max()
        else:
            vmin = int(-1)
            vmax = int(1)
        with col3:
            with sns.axes_style("white"):
                f, (leftAx, rightAx ) = plt.subplots(nrows = 1, ncols=2)
                ax = sns.heatmap(corr, mask = mask, vmax= vmax, vmin = vmin, square=True, cmap = "rocket_r", ax = leftAx, cbar_kws={"shrink": 0.5},  annot=True,annot_kws = {"size": 8}, fmt = '.2f' )
                rightAx.axis('off')
                ax.set_xticklabels(ax.get_xmajorticklabels(), fontsize=8)
                ax.set_yticklabels(ax.get_ymajorticklabels(), fontsize=8)
                cbar = ax.collections[0].colorbar
                cbar.ax.tick_params(labelsize=8)
                st.pyplot(f)

st.set_option('deprecation.showPyplotGlobalUse', False)

 # expander - when clicked, show the raw dataset
with st.expander("See the raw dataset"):
    st.write(df)

st.markdown(
    "This project was created by Maral Doctorarastoo and Joshua Suber for the [Interactive Data Science](https://dig.cmu.edu/ids2022) course at [Carnegie Mellon University](https://www.cmu.edu).")

