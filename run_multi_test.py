#!/usr/bin/env python

import argparse
import os

import docker


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Test script for multi-environment')
    parser.add_argument('--base', choices=docker.base_choices, required=True)
    parser.add_argument('--cuda', choices=docker.cuda_choices, required=True)
    parser.add_argument('--cudnn', choices=docker.cudnn_choices, required=True)
    parser.add_argument('--numpy', choices=['1.9', '1.10', '1.11'],
                        required=True)
    parser.add_argument('--protobuf', choices=['2', '3', 'cpp-3'])
    parser.add_argument('--h5py', choices=['none', '2.5'])
    parser.add_argument('--pillow', choices=['none', '3.3'])
    parser.add_argument('--theano', choices=['none', '0.8'])
    parser.add_argument('--type', choices=['cpu', 'gpu'], required=True)
    parser.add_argument('--cache')
    parser.add_argument('--http-proxy')
    parser.add_argument('--https-proxy')
    parser.add_argument('--no-cache', action='store_true')
    parser.add_argument('--timeout', default='1h')
    parser.add_argument(
        '--gpu-id', type=int,
        help='GPU ID you want to use mainly in the script.')
    parser.add_argument('--interactive', action='store_true')
    args = parser.parse_args()

    conf = {
        'base': args.base,
        'cuda': args.cuda,
        'cudnn': args.cudnn,
        'requires': ['setuptools', 'pip', 'cython==0.24'],
    }
    volume = []
    env = {'CUDNN': conf['cudnn']}

    if args.numpy == '1.9':
        conf['requires'].append('numpy<1.10')
    elif args.numpy == '1.10':
        conf['requires'].append('numpy<1.11')
    elif args.numpy == '1.11':
        conf['requires'].append('numpy<1.12')

    if args.protobuf == '3':
        conf['requires'].append('protobuf<4')
    elif args.protobuf == '2':
        conf['requires'].append('protobuf<3')
    elif args.protobuf == 'cpp-3':
        conf['protobuf-cpp'] = 'protobuf-cpp-3'

    if args.h5py == '2.5':
        conf['requires'].append('h5py<2.6')

    if args.pillow == '3.3':
        conf['requires'].append('pillow<3.4')

    if args.theano == '0.8':
        conf['requires'].append('theano<0.9')

    conf['requires'] += [
        'hacking',
        'nose',
        'mock',
        'coverage',
    ]

    if args.cache:
        volume.append(args.cache)
        env['CUPY_CACHE_DIR'] = os.path.join(args.cache, '.cupy')
        env['CCACHE_DIR'] = os.path.join(args.cache, '.ccache')

    if args.type == 'cpu':
        script = './test_cpu.sh'
    elif args.type == 'gpu':
        script = './test.sh'

    if args.http_proxy:
        conf['http_proxy'] = args.http_proxy
    if args.https_proxy:
        conf['https_proxy'] = args.https_proxy

    if args.interactive:
        docker.run_interactive(
            conf, no_cache=args.no_cache, volume=volume, env=env)
    else:
        docker.run_with(
            conf, script, no_cache=args.no_cache, volume=volume, env=env,
            timeout=args.timeout, gpu_id=args.gpu_id)
