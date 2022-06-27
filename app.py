from io import BytesIO

import pandas as pd
import streamlit as st


@st.cache
def prepare_df_for_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output) as writer:
        df.to_excel(writer, index=False, sheet_name="data")

    data = output.getvalue()

    return data


def main():
    """Main function of the app."""
    st.sidebar.image(r"./images/niva-logo.png", use_column_width=True)
    st.header("Merge logger files")
    st.write(
        "Add logger files using the `Browse` button on the left. "
        "Merged data will be available to download below.\n\n"
        "**Refresh the page** to clear the file list and start again."
    )
    flist = st.sidebar.file_uploader(
        "Select files to merge", accept_multiple_files=True
    )
    if flist:
        df_list = []
        for fpath in flist:
            df = pd.read_csv(
                fpath,
                sep=";",
                skiprows=7,
                encoding="latin1",
                decimal=",",
            )
            df_list.append(df)
        df = pd.concat(df_list, axis="rows")
        df.dropna(subset=["Date"], inplace=True)
        df.index = pd.to_datetime(
            df["Date"] + " " + df["Time"], format="%d/%m/%Y %H:%M"
        )
        df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y").dt.date
        df["Record n"] = df["Record n"].astype(int)
        df.sort_index(inplace=True)
        df.reset_index(inplace=True, drop=True)
        st.dataframe(df)
        excel_bytes = prepare_df_for_download(df)
        st.download_button(
            label="Download data",
            data=excel_bytes,
            file_name="merged_data.xlsx",
        )


if __name__ == "__main__":
    main()
