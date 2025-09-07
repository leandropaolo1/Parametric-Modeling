from typing import Optional

import numpy as np


class Points:
    """
    Manage and align two sets of 3D points:
    - Reference face (slanted in 3D space)
    - Target face (flat in XY plane)
    - A clicked reference point

    Computes normals, axis, angle, and Rodrigues rotation matrix
    for aligning the target face to the reference face.
    """

    def __init__(
        self,
        reference: Optional[np.ndarray] = None,
        target: Optional[np.ndarray] = None,
        point: Optional[np.ndarray] = None,
    ):
        if reference is None or target is None or point is None:
            # Defaults
            self.reference: np.ndarray = np.array(
                [
                    (-113.12865648751726, 4.789457814476987, -270.27419162089467),
                    (-115.07642775687538, 38.80953815277934, -240.5570390438199),
                    (-118.04060161192928, 4.789457814476990, -195.33261472983640),
                    (-118.11044330302204, 20.817561281289972, -194.26704227124210),
                    (-118.50699530542012, 4.255156433468684, -188.21684319920945),
                    (-118.58629913058888, 20.266577164611410, -187.00690690022168),
                ]
            )

            self.target: np.ndarray = np.array(
                [
                    (62.1281, 45.1335, 0),
                    (101.813, 45.1335, 0),
                    (101.813, 67.6384, 0),
                    (62.1281, 67.6384, 0),
                ]
            )

            self.point: np.ndarray = np.array([-115.67, 22.3606, -231.499])
        else:
            self.reference: np.ndarray = reference
            self.target: np.ndarray = target
            self.point: np.ndarray = point

        self._norm("reference")
        self._norm("target")
        self._axis()
        self._angle()

        self.K: np.ndarray = np.array([])

    def compute(self):
        self._norm("reference")
        self._norm("target")
        self._axis()
        self._angle()
        return self._rotation()

    def __str__(self) -> str:
        return f"Points(reference={len(self.reference)} pts, target={len(self.target)} pts, point={self.point})"

    def _norm(self, name):
        att = getattr(self, name)
        v1, v2, v3 = att[:3]
        normal = np.cross(v2 - v1, v3 - v1)
        normal /= np.linalg.norm(normal)
        setattr(self, f"{name}_norm", normal)

    def _axis(self):
        target_norm = getattr(self, "target_norm")
        reference_norm = getattr(self, "reference_norm")
        if target_norm is not None and reference_norm is not None:
            axis = np.cross(target_norm, reference_norm)
            axis_len = np.linalg.norm(axis)
            if axis_len > 1e-8:
                axis /= axis_len
            setattr(self, "axis", axis)
            return axis
        return None

    def _angle(self):
        target_norm = getattr(self, "target_norm")
        reference_norm = getattr(self, "reference_norm")
        if target_norm is not None and reference_norm is not None:
            angle = np.clip(np.dot(target_norm, reference_norm), -1, 1)
            angle = np.arccos(angle)
            setattr(self, "angle", angle)
            return angle
        return None

    def _rotation(self):
        ux, uy, uz = getattr(self, "axis")
        angle = getattr(self, "angle")
        K = np.array([[0, -uz, uy], [uz, 0, -ux], [-uy, ux, 0]])
        I = np.eye(3)
        R = I + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
        setattr(self, "K", K)
        setattr(self, "I", I)
        setattr(self, "R", R)

        return R
