# important libraries 
import streamlit as st
import pandas as pd
import altair as alt

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

# load dataset 
df = load_data()

# introduction and instructions on application 
st.info("This application allows users to explore the question, “How can we categorize different songs based on their audio features? What patterns emerge?” Using the visualization, the user will be able to discover relationships and patterns among a song’s audio features, and how that is correlated to the song’s genre. ")

# default features for scatterplot 

# multiselect to change features on X and Y axis for scatterplot (first choice is X and second choice is Y)
features = st.multiselect('Choose X and Y features to see how they correlate:', ("harmony_mean", "rms_mean", "chroma_stft_mean", "rolloff_mean", "tempo"), default=["chroma_stft_mean", "harmony_mean"])
if len(features) < 2:
    feature_X = "chroma_stft_mean"
    feature_Y = "harmony_mean"
else: 
    feature_X = str(features[0])
    feature_Y = str(features[1])

# dividing the application into columns 
col1, col2 = st.columns((2,1))

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
    , tooltip=['filename','label','chroma_stft_mean', 'harmony_mean']
).properties(
     width=650, height=350
).transform_filter(
    brush
).interactive().add_selection(
    selection
)

# facet charts that show grid of scatterplots for each genre 
facet = alt.Chart(df).mark_point().encode(
    alt.X('chroma_stft_mean:Q'),
    alt.Y('harmony_mean:Q'),
    alt.Color('label:N', legend=alt.Legend(title="Genres")), facet=alt.Facet('label:N', columns=5), 
    tooltip=['filename','label','chroma_stft_mean', 'harmony_mean']
).properties(
    width=110,
    height=110
).transform_filter(brush).interactive()

# set overview intiall to the scatterplot visualization 
overview = scatterplot

####MAYBE ADD A PIE CHART WITH THE PERCENTAGE OF GENRES FROM SELECTION 

# creating strip plot visualizations 
# strip plot visualization for chroma_stft_mean
chart = alt.Chart(df).mark_tick().encode(
    x='chroma_stft_mean', color = alt.condition(brush, "label", alt.value("white"), legend=None),
    tooltip=['filename','label', 'chroma_stft_mean']
).properties(
     width=650, height=45
).add_selection(brush)

# strip plot visualization for rms_mean
chart2 = alt.Chart(df).mark_tick().encode(
    x='rms_mean', color = alt.condition(brush, "label", alt.value("white")), 
    tooltip=['filename','label', 'rms_mean'],
).properties(
     width=650, height=45
).add_selection(brush)

# strip plot visualization for rolloff_mean
chart3 = alt.Chart(df).mark_tick().encode(
    x='rolloff_mean', color = alt.condition(brush, "label", alt.value("white")),
    tooltip=['filename','label', 'rolloff_mean']
).properties(
     width=650, height=45
).add_selection(brush)

# strip plot visualization for harmony_mean
chart4 = alt.Chart(df).mark_tick().encode(
    x='harmony_mean', color = alt.condition(brush, "label", alt.value("white")),
    tooltip=['filename','label', 'harmony_mean']
).properties(
     width=650, height=45
).add_selection(brush)

# strip plot visualization for tempo
chart5 = alt.Chart(df).mark_tick().encode(
    x='tempo', color = alt.condition(brush, "label", alt.value("white")),
    tooltip=['filename','label', 'tempo']
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

    # open and play the audio file 
    audio_file = open('genres_original/'+ genre_selection + '/' + song_selection, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/wav')

    # expander - when clicked, shows the written descriptions of the features 
    with st.expander("See description of features"):
        st.text("chroma_stft: represents information about the classification of pitch and signal structure")
        st.write("rms: a metering tool that measures the average loudness of an audio track within a window of roughly 300 milliseconds")
        st.write("rolloff: denotes the approximate low bass and high treble limits in a frequency response curve, with all frequencies between being those a speaker will play accurately")
        st.write("harmony: the process by which the composition of individual sounds, or superpositions of sounds, is analysed by hearing.")
        st.write("tempo: how fast or slow a piece of music is performed")

    # expander - when clicked, show the raw dataset 
    with st.expander("See the raw dataset"):
        st.write(df)


st.markdown("This project was created by Maral Doctorarastoo and Joshua Suber for the [Interactive Data Science](https://dig.cmu.edu/ids2022) course at [Carnegie Mellon University](https://www.cmu.edu).")

