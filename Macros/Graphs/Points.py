import numpy as np


class Points():
    def __init__(self) -> None:
        pass
        self.reference = np.array([
            (-113.12865648751726,  4.789457814476987, -270.27419162089467),
            (-115.07642775687538, 38.80953815277934, -240.5570390438199),
            (-118.04060161192928,  4.789457814476990, -195.33261472983640),
            (-118.11044330302204, 20.817561281289972, -194.26704227124210),
            (-118.50699530542012,  4.255156433468684, -188.21684319920945),
            (-118.58629913058888, 20.266577164611410, -187.00690690022168)
        ])

        self.target = np.array([
            (62.1281, 45.1335, 0),
            (101.813, 45.1335, 0),
            (101.813, 67.6384, 0),
            (62.1281, 67.6384, 0)
        ])

        self.point = np.array([-115.67, 22.3606, -231.499])

        self._norm("reference")
        self._norm("target")
        self._axis()
        self._angle()
        
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
        if target_norm and reference_norm: 
            axis = np.cross(target_norm, reference_norm)
            axis_len = np.linalg.norm(axis)
            if axis_len > 1e-8:
                axis /= axis_len
            setattr(self, "rotation", axis)
            return axis
        return None
    
    def _angle(self):
        target_norm = getattr(self, "target_norm")
        reference_norm = getattr(self, "reference_norm")
        if target_norm and reference_norm:
            angle = np.clip(np.dot(target_norm, reference_norm), -1, 1)
            angle = np.arccos(angle)
            setattr(self, "angle", angle)
            return angle
        return None

    def rotation(self):
        

