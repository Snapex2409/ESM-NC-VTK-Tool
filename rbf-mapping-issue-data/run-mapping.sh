#!/bin/bash

precice-aste-run -p A --mesh ./nogt_sinusoid --data "eval"&
precice-aste-run -p B --mesh ./icos_masked_by_nogt --output ./nogt_to_icos_masked_by_nogt_sinusoid --data "eval"
