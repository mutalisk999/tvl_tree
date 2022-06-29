#!/usr/bin/env python
# encoding: utf-8


class TvlTreeNode(object):
    def __init__(self, _parent_node, _children_nodes, _user_addr_biz):
        self.parent_node: TvlTreeNode = _parent_node
        self.children_nodes = _children_nodes
        self.user_addr_biz = _user_addr_biz
        self.accumulative_tvl = 0
        self.tvl = 0


def create_new_root_node() -> TvlTreeNode:
    return TvlTreeNode(None, [], "root")


def create_new_node(_parent_node, _user_addr_biz) -> TvlTreeNode:
    return TvlTreeNode(_parent_node, [], _user_addr_biz)
