import logging

import click
import tqdm
from rich.logging import RichHandler

from roughml.data.generators import (
    BesselNonGaussianSurfaceGenerator,
    NonGaussianSurfaceGenerator,
)
from roughml.data.sets import NanoroughSurfaceDataset

logger = logging.getLogger(__name__)


def get_standard_generator(config):
    return NonGaussianSurfaceGenerator(
        n_points=config["number_of_points"],
        rms=config["rms"],
        skewness=config["skewness"],
        kurtosis=config["kurtosis"],
        corlength_x=config["correlation_lengths"][0],
        corlength_y=config["correlation_lengths"][1],
        alpha=config["alpha"],
    )


def get_besel_generator(config, betas):
    return BesselNonGaussianSurfaceGenerator(
        n_points=config["number_of_points"],
        rms=config["rms"],
        skewness=config["skewness"],
        kurtosis=config["kurtosis"],
        corlength_x=config["correlation_lengths"][0],
        corlength_y=config["correlation_lengths"][1],
        alpha=config["alpha"],
        beta_x=betas[0],
        beta_y=betas[1],
    )


def generate(generator, dataset_size, save_path):
    surfaces = []
    for surface in tqdm.tqdm(generator(dataset_size)):
        surfaces.append(surface)

    dataset = NanoroughSurfaceDataset.from_list(surfaces)

    dataset.to_pt(save_path)


@click.group()
@click.option(
    "-s",
    "--surfaces",
    "surfaces",
    required=False,
    type=click.INT,
    help="The number of surfaces that should be generated",
    default=10,
)
@click.option(
    "-d",
    "--dataset",
    "dataset_path",
    required=True,
    type=click.Path(exists=False, dir_okay=False),
    help="Where to save the resulting dataset",
)
@click.option(
    "-l",
    "--log",
    "logging_level",
    required=False,
    type=click.Choice(
        [
            "CRITICAL",
            "FATAL",
            "ERROR",
            "WARNING",
            "WARN",
            "INFO",
            "DEBUG",
            "NOTSET",
        ],
        case_sensitive=False,
    ),
    help="Specify the logging level",
    default="NOTSET",
)
@click.option(
    "-n",
    "--number-of-points",
    "number_of_points",
    required=False,
    type=click.INT,
    help="The (root of the) number of points to be used",
    default=128,
)
@click.option(
    "-r",
    "--rms",
    "rms",
    required=False,
    type=click.INT,
    help="The RMS of the nanorough surface",
    default=1,
)
@click.option(
    "-s",
    "--skewness",
    "skewness",
    required=False,
    type=click.INT,
    help="The skewness of the nanorough surface",
    default=0,
)
@click.option(
    "-k",
    "--kurtosis",
    "kurtosis",
    required=False,
    type=click.INT,
    help="The kurtosis of the nanorough surface",
    default=0,
)
@click.option(
    "-c",
    "--correlation-lengths",
    "correlation_lengths",
    required=False,
    type=(int, int),
    help="The correlation lengths of the nanorough surface",
    default=(4, 4),
)
@click.option(
    "-a",
    "--alpha",
    "alpha",
    required=False,
    type=click.INT,
    help="The alpha of the nanorough surface",
    default=1,
)
@click.pass_context
def dataset(
    ctx,
    surfaces,
    dataset_path,
    logging_level,
    number_of_points,
    rms,
    skewness,
    kurtosis,
    correlation_lengths,
    alpha,
):
    """Generate datasets consisting of nanorough surfaces"""
    ctx.obj = {
        "surfaces": surfaces,
        "dataset_path": dataset_path,
        "number_of_points": number_of_points,
        "rms": rms,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "correlation_lengths": correlation_lengths,
        "alpha": alpha,
    }

    logging.basicConfig(
        level=logging_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


@dataset.command()
@click.pass_obj
def standard(config):
    """Generate a dataset consisting of non-gaussian surfaces"""
    generator = get_standard_generator(config)

    generate(generator, config["surfaces"], config["dataset_path"])


@dataset.command()
@click.option(
    "-b",
    "--betas",
    "betas",
    required=False,
    type=(int, int),
    help="The betas of the nanorough surface",
    default=(1, 1),
)
@click.pass_obj
def besel(config, betas):
    """Generate a dataset consisting of non-gaussian surfaces utilizing a bessel function"""
    generator = get_besel_generator(config, betas)

    generate(generator, config["surfaces"], config["dataset_path"])


if __name__ == "__main__":
    dataset()