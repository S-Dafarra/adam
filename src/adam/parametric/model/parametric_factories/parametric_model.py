import pathlib
from typing import List

import urdf_parser_py.urdf

from adam.core.spatial_math import SpatialMath
from adam.model import ModelFactory, StdJoint, StdLink, Link, Joint
from adam.parametric.model import ParmetricJoint, ParametricLink


class URDFParametricModelFactory(ModelFactory):
    """This factory generates robot elements from urdf_parser_py parametrized w.r.t. link lengths and densities

    Args:
        ModelFactory: the Model factory
    """

    def __init__(
        self,
        path: str,
        math: SpatialMath,
        links_name_list: List,
        length_multiplier,
        densities,
    ):
        self.math = math
        if type(path) is not pathlib.Path:
            path = pathlib.Path(path)
        if not path.exists():
            raise FileExistsError(path)
        self.links_name_list = links_name_list
        self.urdf_desc = urdf_parser_py.urdf.URDF.from_xml_file(path)
        self.name = self.urdf_desc.name
        self.length_multiplier = length_multiplier
        self.densities = densities

    def get_joints(self) -> List[Joint]:
        """
        Returns:
            List[Joint]: build the list of the joints
        """
        return [self.build_joint(j) for j in self.urdf_desc.joints]

    def get_links(self) -> List[Link]:
        """
        Returns:
            List[Link]: build the list of the links
        """
        return [
            self.build_link(l) for l in self.urdf_desc.links if l.inertial is not None
        ]

    def get_frames(self) -> List[StdLink]:
        """
        Returns:
            List[Link]: build the list of the links
        """
        return [self.build_link(l) for l in self.urdf_desc.links if l.inertial is None]

    def build_joint(self, joint: urdf_parser_py.urdf.Joint) -> Joint:
        """
        Args:
            joint (Joint): the urdf_parser_py joint

        Returns:
            StdJoint/ParametricJoint: our joint representation
        """
        if joint.parent in self.links_name_list:
            index_link = self.links_name_list.index(joint.parent)
            link_parent = self.get_element_by_name(joint.parent)
            parent_link_parametric = ParametricLink(
                link_parent,
                self.math,
                self.length_multiplier[index_link],
                self.densities[index_link],
            )
            return ParmetricJoint(joint, self.math, parent_link_parametric)

        return StdJoint(joint, self.math)

    def build_link(self, link: urdf_parser_py.urdf.Link) -> Link:
        """
        Args:
            link (Link): the urdf_parser_py link

        Returns:
            StdLink/ParametricLink: our link representation
        """
        if link.name in self.links_name_list:
            index_link = self.links_name_list.index(link.name)
            return ParametricLink(
                link,
                self.math,
                self.length_multiplier[index_link],
                self.densities[index_link],
            )
        return StdLink(link, self.math)

    def get_element_by_name(self, link_name):
        """
        Args:
            link_name (Link): the link name

        Returns:
            Link: the urdf parser link object associated to the link name
        """
        link_list = [
            corresponding_link
            for corresponding_link in self.urdf_desc.links
            if corresponding_link.name == link_name
        ]
        if len(link_list) != 0:
            return link_list[0]
        else:
            return None
