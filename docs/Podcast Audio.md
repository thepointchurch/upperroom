# Uploading Sermon Audio

## Processing the Audio

The audio needs to be trimmed, normalised, and compressed to an MP3 file.

### Trimming

1. Open the WAV file in Audacity.

2. Find the start point of the sermon content. You can remove extraneous comments and noises.

3. Click and drag to select all the audio before this start point.

4. Choose `Edit` → `Cut` (or `Ctrl-X`) to trim the start.

5. Do the same at the end of the recording to remove extraneous audio after the end of the sermon.

### Normalising

Normalising will adjust the loudness of the recording to a relatively standard level.

1. Choose `Select` → `All`.

2. Choose `Effect` → `Normalize`.

    Leave what are probably the default options:

    * `Remove DC offset` → `yes`
    * `Normalize peak amplitude` → `1.5`
    * `Normalize stereo channels independently` → `no`

    Select `OK`.

### Compression

Normal spoken voice does not need the sample rate or bandwidth required by music, so compromises can be made to produce a very small output without significantly compromising audio quality.

1. Set the `Project Rate` to `22050`. This is set at the bottom-left of the main screen.

2. Choose `File` → `Export` → `Export as MP3`.

    Use the following options:

    * `Bit Rate Mode` → `Variable`
    * `Quality` → `45-85 kbps`
    * `Variable Speed` → `Fast`
    * `Channel Mode` → `Force export to mono`

    Select `Save`.

3. Set file metadata:

    * `Artist Name` → speaker's full name
    * `Track Title` → sermon title
    * `Album Title` → `The Point Church Sermons`
    * `Year` → date of the sermon in the format `YYYY-MM-DD`
    * `Genre` → `Podcast`

    Select `OK`.

## Uploading the Audio

To upload the audio to the website, you will create a `Resource` with an `Attachment`.

1. Log into the website and go to the admin site at [https://thepoint.org.au/admin/](https://thepoint.org.au/admin/).

2. Under `Resources` → `Resources` select `Add`.

3. Fill in the details as follows:

    * `Title` → sermon title
    * `Slug` → This will be auto-completed based on the title. **Make sure you add the year of the sermon to the start of the `Slug`**. It should look something like `2019-love-one-another`. This is important because the `Slug` must be unique across _all_ resources, but it is conceivable that sermon titles may not always be unique.
    * Leave the `Description` and `Body` empty unless there is something obvious or compelling to include.
    * Under `Tags` select `Sermons`. **Don't forget this step!**
    * Under `Author` select the name of the preacher, if they are present. Leave `Show author` checked.
    * Leave `Featured` alone.
    * Under `Advanced` select:
        * `Published` → `yes`
        * If you are uploading on the same day the sermon was preached you can leave `Published` empty, otherwise select the `Date` and `Time` of the sermon.
        * `Private` → `no`
        * `Show date` → `yes`
        * Leave `Parent` empty.
    * Under `Attachments` select `Add another Attachment`:
        * `Title` → same as the sermon title
        * `Slug` → this needn't include the year as for the `Resource`'s `Slug`, but it must be different from other `Attachment`s for this `Resource`.
        * `File` → choose the MP3 file exported from Audacity above.
        * `Kind` → `Alternate`
    * If you have a copy of slides from the sermon presentation, or any other materials to include, add them as another attachment (also `Kind` → `Alternate`), preferably as a PDF file. Remember the `Slug` will need to be unique within this `Resource`.
    * Click `Save`
