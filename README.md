Fine-grained Sentiment Analysis on User Reviews
-----------------------------------------------

This is a solution for the [Fine-grained Sentiment Analysis of User Reviews](https://challenger.ai/competition/fsauor2018) challenge
from AI Challenger.

## Dataset

The original Chinese dataset can be [downloaded here](https://drive.google.com/file/d/1YYRWKJmahhVW7ZmzGeEtlKqDl4h-v0wG/view).

We also translated 1/10 of the training data to English, using Google Translate API.
The English dataset is already included in the repository.

## Getting Started

- Put data into the `data` folder, or
- `cp config.py config_local.py`, and edit the file paths in `config_local.py`.

Make sure you have the required Python packages installed.

```
pip install -r requirements.txt
```

### Train Models

Checkout `2. Model Selection.ipynb` in `notebooks`.

Or run:

```bash
./fgclassifer/train.py -c LDA
```

### Visualize the Results

We've build a visualization tool to evaluate the performance of different models.
You can dive into a single review and check why a model predicted the given results
by rerun the prediction on arbitrary sentence segments in a review. The visualization
also allows you to see which sentiment aspects the model find it particularly difficult
to predict.

For a detailed description of how we designed and implemented the visualization, [check here](https://docs.google.com/document/d/1T6TkbO62Rf3h5-jnMj7DGh_AKYtkmPCvAuUN7Adgvb0/edit).
A demo of the visualization can be found here: http://review-sentiments.yjc.me/


```
python app.py --port 500
```

Change `--port` as your like.

## Deploy

The visualization can be easily deployed via [Dokku](https://github.com/dokku/dokku).
Just make sure to upload your pre-trained models to the appropriate
[persistent storage](https://github.com/dokku/dokku/blob/master/docs/advanced-usage/persistent-storage.md)
directory on the host machine.

Here's a list of Dokku commands you can probably use:

```bash
alias dokku="ssh dokku@your-host"

git remote add dokku dokku@your-host/review-sentiments
git push dokku  # first push automatically creates the app

dokku config:set review-sentiments FLASK_SECRECT_KEY=`openssl rand -base64 16`
dokku config:set review-sentiments DATA_ROOT=/opt/storage

# For storing pre-trained models
dokku storage:mount review-sentiments /var/lib/dokku/data/storage/review-sentiments:/opt/storage
```

Then upload the dataset and the pre-trained models to your host:

```
scp -r data/* /var/lib/dokku/data/storage/review-sentiments
```

You can also download pre-trained models [here](http://review-sentiments.yjc.me/files/models/).


## Local Development


### With Docker

I recommend using the Docker image:

```
docker build -t ktmud/fgclassifier .
docker-compose up
```

Note that `docker-compose` will add storage mapping between
your host machine and the Docker container, and set required
variables.

You need to set DATA_ROOT to `/opt/storage/` and
create a `/opt/storage/` folder on your
host machine and make user it is accessible by Docker.

### Without Docker

To run the app without Docker, install the required packages 
via `requirements.txt`, then make sure the data (and pre-trained models)
are in your `DATA_ROOT` (take a look at `config.py` for how file paths are
defined).

```
pip install -r requirement.txt
export DATA_ROOT="./data"
python fgclassifier/prepare.py
python app.py
```
