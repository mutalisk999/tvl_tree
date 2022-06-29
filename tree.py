#!/usr/bin/env python
# encoding: utf-8


from tree_node import TvlTreeNode
from tree_node import create_new_root_node, create_new_node


class TvlTree(object):
    def __init__(self):
        # 创建一个根节点
        self.tvl_tree_root: TvlTreeNode = create_new_root_node()
        self.full_data_map = dict()
        # 根节点存入map
        self.full_data_map["root"] = self.tvl_tree_root
        # 用户tvl map
        self.tvl_map = dict()
        # 用户累计tvl map
        self.accumulative_tvl_map = dict()

    def add_node(self, _user_addr_biz, _parent_addr_biz):
        # 父节点必须存在
        v = self.full_data_map.get(_parent_addr_biz)
        if v is None:
            raise Exception("父节点不存在")
        # 新节点必须不存在
        vv = self.full_data_map.get(_user_addr_biz)
        if vv is not None:
            raise Exception("新节点已存在")

        # 创建一个新的子节点
        node = create_new_node(v, _user_addr_biz)
        # 父节点中增加一个子节点
        self.full_data_map[_parent_addr_biz].children_nodes.append(node)
        # 子节点存入map
        self.full_data_map[_user_addr_biz] = node

    def move_node(self, _user_addr_biz, _parent_addr_biz_new):
        # 需要移动的节点必须存在
        v = self.full_data_map.get(_user_addr_biz)
        if v is None:
            raise Exception("需要移动的节点不存在")
        # 目标父节点必须存在
        vv = self.full_data_map.get(_parent_addr_biz_new)
        if vv is None:
            raise Exception("目标父节点不存在")

        # 原先父节点删掉这个子节点
        v.parent_node.children_nodes.remove(v)
        # 设置此节点的新父节点
        v.parent_node = vv
        # 父节点将此节点设置到子节点队列中
        vv.children_nodes.append(v)

    def init_from_batch_data(self, _batch_data):
        # _batch_data 格式为 [ (user_addr, parent_addr), (user_addr, parent_addr), (user_addr, parent_addr), ... ]
        parent_to_user_map = dict()
        for data in _batch_data:
            if parent_to_user_map.get(data[1]) is None:
                parent_to_user_map[data[1]] = [data[0]]
            parent_to_user_map[data[1]].append(data[0])

        # 从 parent_addr 为 root开始
        v = parent_to_user_map.get("root")
        if v is None:
            raise Exception("父节点地址为root的节点不存在")
        open_table = [(a, "root") for a in v]

        # 一层一层将父子节点的关系存入open_table,然后将节点挂载到树上
        while len(open_table) > 0:
            t = open_table.pop(0)
            self.add_node(t[0], t[1])

            vv = parent_to_user_map.get(t[0])
            if vv is not None:
                open_table.extend([(aa, t[0]) for aa in vv])

    def init_root_accumulative_tvl_from_batch_tvl_data(self, _tvl_batch_data):
        # _tvl_batch_data 格式为 [ (user_addr, tvl_value), ... ]
        user_addr_to_tvl_map = dict()
        for data in _tvl_batch_data:
            user_addr_to_tvl_map[data[0]] = data[1]

        def calc_node_accumulative_tvl(_user_addr, _user_addr_to_tvl_map):
            # 避免无意义递归, 如果缓存中已经存在, 则从缓存中获取
            if _user_addr in self.accumulative_tvl_map.keys():
                return self.accumulative_tvl_map[_user_addr]

            # 用户地址必须存在于树节点上
            v = self.full_data_map.get(_user_addr)
            if v is None:
                raise Exception("节点地址不存在")

            # user_addr_to_tvl_map 中找不到就是 0
            node_tvl = _user_addr_to_tvl_map.get(_user_addr)
            if node_tvl is None:
                node_tvl = 0

            # 没有子节点, 则返回本节点的 tvl
            # 如果存在子节点, 则返回 本节点的tvl 和子节点累计tvl的和
            if len(v.children_nodes) == 0:
                accumulative_tvl = node_tvl
            else:
                accumulative_tvl = node_tvl + sum(
                    [calc_node_accumulative_tvl(node.user_addr_biz) for node in v.children_nodes])

            # 记入tree_node和缓存
            v.accumulative_tvl = accumulative_tvl
            self.accumulative_tvl_map[v.user_addr_biz] = accumulative_tvl

            v.tvl = node_tvl
            self.tvl_map[v.user_addr_biz] = node_tvl

            return accumulative_tvl

        self.tvl_map.clear()
        self.accumulative_tvl_map.clear()
        calc_node_accumulative_tvl("root", user_addr_to_tvl_map)
