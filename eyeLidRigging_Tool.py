import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as api

class eyeLidRig(object):
    WindowName = 'eyeLidRiggingTool'
    if cmds.window(WindowName, q=True, ex=True):
        cmds.deleteUI(WindowName)

    def baseWindow(self):
        cmds.window(self.WindowName, t='eyeLidRigging Tool v3', s=False)
        cmds.window(self.WindowName, e=True, wh=(500, 330))
        self.Layouts()
        cmds.showWindow(self.WindowName)


class setLayouts(eyeLidRig):
    def __init__(self):
        self.names = None

    def Layouts(self):
        cmds.dR_selConstraintOff()
        cmds.symmetricModelling(e=True, symmetry=False)
        colum1 = cmds.columnLayout(adj=True, bgc=(0.169, 0.169, 0.169))
        titleText = cmds.text(l='eyeLidRigging Tool', h=100, bgc=(0.43, 0.43, 0.43), fn='fixedWidthFont')
        topSep = cmds.separator(h=40)
        baseForm = cmds.formLayout()
        self.gredient = cmds.gradientControlNoAttr('gredientSkinWeight', w=300, h=150, dc=self.setWeightCom)
        cmds.optionVar(rm='falloffCurveOptionVar')
        cmds.optionVar(stringValueAppend=['falloffCurveOptionVar', '1,0,3'])
        cmds.optionVar(stringValueAppend=['falloffCurveOptionVar', '0,1,3'])
        cmds.gradientControlNoAttr(self.gredient, e=True, ov='falloffCurveOptionVar')
        txt2 = cmds.text(l='|---------|---------|---------|---------|', fn='fixedWidthFont')
        setWeight = cmds.button(l='refresh Weight', bgc=(0.420, 0.87, 0.9), c=self.setWeightCom)
        colum2 = cmds.columnLayout(adj=True)
        self.names = cmds.textFieldGrp(l='name:', cw2=(30, 150), pht='...', h=30)
        cmds.separator(h=10)
        rowColum1 = cmds.rowColumnLayout(numberOfRows=1)
        cmds.text(l='edgeLoop:  ', h=10)
        self.radiu = cmds.radioButtonGrp(labelArray2=['on', 'off'], numberOfRadioButtons=2, sl=2, cw2=(80, 10),
                                         cc1=self.loopOn, cc2=self.loopOff)
        rowColum2 = cmds.rowColumnLayout(p=colum2, numberOfRows=1)
        outer = cmds.button(p=rowColum2, l='outer', w=57, bgc=(0.85, 0.65, 0.0), c=self.CreateOuterCrv)
        cmds.text(l='')
        outer = cmds.button(p=rowColum2, l='main', w=57, bgc=(0.85, 0.65, 0.0), c=self.CreateMainCrv)
        cmds.text(l='')
        outer = cmds.button(p=rowColum2, l='inner', w=57, bgc=(0.85, 0.65, 0.0), c=self.CreateInnerCrv)
        cmds.separator(p=colum2, h=10)
        rowColum3 = cmds.rowColumnLayout(p=colum2, numberOfRows=1)
        cmds.button(p=rowColum3, l='setupRig', w=120, bgc=(0.420, 0.87, 0.9), c=self.createSpaceJnts)
        self.mirrorChesk = cmds.checkBoxGrp(p=rowColum3, l='mirror:', cw2=(50, 10), v1=True)
        cmds.formLayout(baseForm, e=True,
                        attachForm=[(self.gredient, 'top', 0), (txt2, 'left', 5), (setWeight, 'left', 5),
                                    (setWeight, 'right', 5), (colum2, 'left', 0), (colum2, 'right', 50)],
                        attachControl=[(txt2, 'top', -10, self.gredient), (setWeight, 'top', 5, txt2),
                                       (colum2, 'left', 5, self.gredient)]
                        )


class controls(setLayouts):

    def loopOn(self, *args):
        cmds.dR_selConstraintEdgeLoop()
        mel.eval("print dR_selConstraintEdgeLoop")
        print ('my Tools')

    def loopOff(self, *args):
        cmds.dR_selConstraintOff()
        mel.eval("print dR_selConstraintOff")

    def CreateOuterCrv(self, *args):
        if cmds.textFieldGrp(self.names, q=True, tx=True) == '':
            mel.eval("print please_Enter_a_name")
        elif cmds.textFieldGrp(self.names, q=True, tx=True):
            selEdge = cmds.ls(sl=True, fl=True)
            if cmds.xform(selEdge[0], q=True, ws=True, t=True)[0] > 0:
                self.judge_LR = 'l_'
            elif cmds.xform(selEdge[0], q=True, ws=True, t=True)[0] < 0:
                self.judge_LR = 'r_'
            self.name = cmds.textFieldGrp(self.names, q=True, tx=True)
            self.outerUpCrv = self.judge_LR + self.name + 'OuterLidUp_crv'
            self.outerLowCrv = self.judge_LR + self.name + 'OuterLidLow_crv'
            if cmds.ls(sl=True) == []:
                mel.eval("print please_Select_Edge")
            else:
                cmds.polyToCurve(form=2, degree=1, conformToSmoothMeshPreview=False, n=self.judge_LR + 'lid_crv',
                                 ch=False)
                msel = api.MSelectionList()
                msel.add(self.judge_LR + 'lid_crv')
                dagPath = msel.getDagPath(0)
                MFn_Crv = api.MFnNurbsCurve(dagPath)

                getPoss = MFn_Crv.cvPositions(api.MSpace.kWorld)
                posList = [x for x in getPoss]
                MinoutCornerX = min([x[0] for x in getPoss])
                MaxoutCornerX = max([x[0] for x in getPoss])
                for outPos in posList:
                    if outPos[0] == MinoutCornerX and outPos[0] > 0:
                        outCornerVtx_Pos = outPos

                    elif outPos[0] == MaxoutCornerX and outPos[0] < 0:
                        outCornerVtx_Pos = outPos

                toler = MFn_Crv.distanceToPoint(outCornerVtx_Pos, api.MSpace.kObject)
                getDir = MFn_Crv.getParamAtPoint(outCornerVtx_Pos, toler, api.MSpace.kObject)
                cmds.select(self.judge_LR + 'lid_crv.u[%s]' % getDir, r=True)
                mel.eval("moveNurbsCurveSeam")

                getSpans = cmds.getAttr(self.judge_LR + 'lid_crvShape.spans')
                if MFn_Crv.cvPosition(1, api.MSpace.kObject).y < MFn_Crv.cvPosition(getSpans, api.MSpace.kObject).y:
                    cmds.reverseCurve(self.judge_LR + 'lid_crv', ch=False, rpo=1)
                upLipCvPos = []
                upLipCvK = []
                for posIn in range(0, (int(getSpans / 2) + 1)):
                    upLipCvPos.append(cmds.pointPosition(self.judge_LR + 'lid_crv.cv[%s]' % posIn, w=True))
                    upLipCvK.append(posIn)
                cmds.curve(d=1, p=upLipCvPos, k=upLipCvK, n=self.judge_LR + self.name + 'OuterLidUp_crv')
                cmds.rename(cmds.listRelatives(self.judge_LR + self.name + 'OuterLidUp_crv'),
                            self.judge_LR + self.name + 'OuterLidUp_crvShape')
                self.outerUpCrv = self.judge_LR + self.name + 'OuterLidUp_crv'
                cmds.setAttr(self.judge_LR + self.name + 'OuterLidUp_crvShape.dispCV', True)

                self.polyObject = selEdge[0].split('.')[0]

                outerUpLidIDList = api.MSelectionList()
                outerUpLidIDList.add(self.polyObject)
                outerUpLidIDList.add(self.judge_LR + self.name + 'OuterLidUp_crv')
                getPolyDag = outerUpLidIDList.getDagPath(0)
                getCvDag = outerUpLidIDList.getDagPath(1)
                MFn_mesh = api.MFnMesh(getPolyDag)
                MIt_mesh = api.MItMeshFaceVertex(getPolyDag)
                MFn_NurbsCurve = api.MFnNurbsCurve(getCvDag)

                self.lidOuterUpList = []
                cvPositions = [cvMPos for cvMPos in MFn_NurbsCurve.cvPositions(api.MSpace.kObject)]
                for CVPos in cvPositions:
                    Mpoint, faceID = MFn_mesh.getClosestPoint(CVPos, api.MSpace.kObject)
                    faceVtxCount = MFn_mesh.polygonVertexCount(faceID)

                    for s in range(faceVtxCount):
                        MIt_mesh.setIndex(faceID, s)
                        getFaceId = MIt_mesh.vertexId()
                        if MFn_mesh.getPoint(getFaceId) == Mpoint:
                            self.lidOuterUpList.append(getFaceId)

                getSpans = cmds.getAttr(self.judge_LR + 'lid_crvShape.spans')
                if MFn_Crv.cvPosition(1, api.MSpace.kObject).y > MFn_Crv.cvPosition(getSpans, api.MSpace.kObject).y:
                    cmds.reverseCurve(self.judge_LR + 'lid_crv', ch=False, rpo=1)
                lowLipCvPos = []
                lowLipCvK = []
                for posIn in range(0, (int(getSpans / 2) + 1)):
                    lowLipCvPos.append(cmds.pointPosition(self.judge_LR + 'lid_crv.cv[%s]' % posIn, w=True))
                    lowLipCvK.append(posIn)
                cmds.curve(d=1, p=lowLipCvPos, k=lowLipCvK, n=self.judge_LR + self.name + 'OuterLidLow_crv')
                cmds.rename(cmds.listRelatives(self.judge_LR + self.name + 'OuterLidLow_crv'),
                            self.judge_LR + self.name + 'OuterLidLow_crvShape')
                self.outerLowCrv = self.judge_LR + self.name + 'OuterLidLow_crv'
                cmds.setAttr(self.judge_LR + self.name + 'OuterLidLow_crvShape.dispCV', True)

                outerLowLidIDList = api.MSelectionList()
                outerLowLidIDList.add(self.polyObject)
                outerLowLidIDList.add(self.judge_LR + self.name + 'OuterLidLow_crv')
                getPolyDag = outerLowLidIDList.getDagPath(0)
                getCvDag = outerLowLidIDList.getDagPath(1)
                MFn_mesh = api.MFnMesh(getPolyDag)
                MIt_mesh = api.MItMeshFaceVertex(getPolyDag)
                MFn_NurbsCurve = api.MFnNurbsCurve(getCvDag)

                self.lidOuterLowList = []
                cvPositions = [cvMPos for cvMPos in MFn_NurbsCurve.cvPositions(api.MSpace.kObject)]
                for CVPos in cvPositions:
                    Mpoint, faceID = MFn_mesh.getClosestPoint(CVPos, api.MSpace.kObject)
                    faceVtxCount = MFn_mesh.polygonVertexCount(faceID)

                    for s in range(faceVtxCount):
                        MIt_mesh.setIndex(faceID, s)
                        getFaceId = MIt_mesh.vertexId()
                        if MFn_mesh.getPoint(getFaceId) == Mpoint:
                            if getFaceId in self.lidOuterUpList:
                                continue
                            self.lidOuterLowList.append(getFaceId)

                if 'OtherCrv_grp' in cmds.ls():
                    pass
                elif 'OtherCrv_grp' not in cmds.ls():
                    self.OtherCrvGrp = cmds.group(em=True, n='OtherCrv_grp')
                cmds.parent(self.outerUpCrv, self.OtherCrvGrp)
                cmds.parent(self.outerLowCrv, self.OtherCrvGrp)
                cmds.delete(self.judge_LR + 'lid_crv')
                cmds.select(cl=True)

    def CreateMainCrv(self, *args):
        if cmds.textFieldGrp(self.names, q=True, tx=True) == '':
            mel.eval("print please_Enter_a_name")
        elif cmds.textFieldGrp(self.names, q=True, tx=True):
            self.name = cmds.textFieldGrp(self.names, q=True, tx=True)
            self.mainUpCrv = self.judge_LR + self.name + '_mainLidUp_crv'
            self.mainLowCrv = self.judge_LR + self.name + '_mainLidLow_crv'
            if cmds.ls(sl=True) == []:
                mel.eval("print please_Select_Edge")
            else:
                selEdge = cmds.ls(sl=True, fl=True)
                cmds.polyToCurve(form=2, degree=1, conformToSmoothMeshPreview=False, n=self.judge_LR + 'lid_crv',
                                 ch=False)
                msel = api.MSelectionList()
                msel.add(self.judge_LR + 'lid_crv')
                dagPath = msel.getDagPath(0)
                MFn_Crv = api.MFnNurbsCurve(dagPath)

                getPoss = MFn_Crv.cvPositions(api.MSpace.kWorld)
                posList = [x for x in getPoss]
                MinoutCornerX = min([x[0] for x in getPoss])
                MaxoutCornerX = max([x[0] for x in getPoss])
                for outPos in posList:
                    if outPos[0] == MinoutCornerX and outPos[0] > 0:
                        outCornerVtx_Pos = outPos

                    elif outPos[0] == MaxoutCornerX and outPos[0] < 0:
                        outCornerVtx_Pos = outPos

                toler = MFn_Crv.distanceToPoint(outCornerVtx_Pos, api.MSpace.kObject)
                getDir = MFn_Crv.getParamAtPoint(outCornerVtx_Pos, toler, api.MSpace.kObject)
                cmds.select(self.judge_LR + 'lid_crv.u[%s]' % getDir, r=True)
                mel.eval("moveNurbsCurveSeam")

                getSpans = cmds.getAttr(self.judge_LR + 'lid_crvShape.spans')
                if MFn_Crv.cvPosition(1, api.MSpace.kObject).y < MFn_Crv.cvPosition(getSpans, api.MSpace.kObject).y:
                    cmds.reverseCurve(self.judge_LR + 'lid_crv', ch=False, rpo=1)
                upLipCvPos = []
                upLipCvK = []
                for posIn in range(0, (int(getSpans / 2) + 1)):
                    upLipCvPos.append(cmds.pointPosition(self.judge_LR + 'lid_crv.cv[%s]' % posIn, w=True))
                    upLipCvK.append(posIn)
                cmds.curve(d=1, p=upLipCvPos, k=upLipCvK, n=self.judge_LR + self.name + 'MainLidUp_crv')
                cmds.rename(cmds.listRelatives(self.judge_LR + self.name + 'MainLidUp_crv'),
                            self.judge_LR + self.name + 'MainLidUp_crvShape')
                self.mainUpCrv = self.judge_LR + self.name + 'MainLidUp_crv'
                cmds.setAttr(self.judge_LR + self.name + 'MainLidUp_crvShape.dispCV', True)

                MainUpLidIDList = api.MSelectionList()
                MainUpLidIDList.add(self.polyObject)
                MainUpLidIDList.add(self.judge_LR + self.name + 'MainLidUp_crv')
                getPolyDag = MainUpLidIDList.getDagPath(0)
                getCvDag = MainUpLidIDList.getDagPath(1)
                MFn_mesh = api.MFnMesh(getPolyDag)
                MIt_mesh = api.MItMeshFaceVertex(getPolyDag)
                MFn_NurbsCurve = api.MFnNurbsCurve(getCvDag)

                self.lidMainUpList = []
                cvPositions = [cvMPos for cvMPos in MFn_NurbsCurve.cvPositions(api.MSpace.kObject)]
                for CVPos in cvPositions:
                    Mpoint, faceID = MFn_mesh.getClosestPoint(CVPos, api.MSpace.kObject)
                    faceVtxCount = MFn_mesh.polygonVertexCount(faceID)

                    for s in range(faceVtxCount):
                        MIt_mesh.setIndex(faceID, s)
                        getFaceId = MIt_mesh.vertexId()
                        if MFn_mesh.getPoint(getFaceId) == Mpoint:
                            self.lidMainUpList.append(getFaceId)

                getSpans = cmds.getAttr(self.judge_LR + 'lid_crvShape.spans')
                if MFn_Crv.cvPosition(1, api.MSpace.kObject).y > MFn_Crv.cvPosition(getSpans, api.MSpace.kObject).y:
                    cmds.reverseCurve(self.judge_LR + 'lid_crv', ch=False, rpo=1)
                lowLipCvPos = []
                lowLipCvK = []
                for posIn in range(0, (int(getSpans / 2) + 1)):
                    lowLipCvPos.append(cmds.pointPosition(self.judge_LR + 'lid_crv.cv[%s]' % posIn, w=True))
                    lowLipCvK.append(posIn)
                cmds.curve(d=1, p=lowLipCvPos, k=lowLipCvK, n=self.judge_LR + self.name + 'MainLidLow_crv')
                cmds.rename(cmds.listRelatives(self.judge_LR + self.name + 'MainLidLow_crv'),
                            self.judge_LR + self.name + 'MainLidLow_crvShape')
                self.mainLowCrv = self.judge_LR + self.name + 'MainLidLow_crv'
                cmds.setAttr(self.judge_LR + self.name + 'MainLidLow_crvShape.dispCV', True)

                MainLowLidIDList = api.MSelectionList()
                MainLowLidIDList.add(self.polyObject)
                MainLowLidIDList.add(self.judge_LR + self.name + 'MainLidLow_crv')
                getPolyDag = MainLowLidIDList.getDagPath(0)
                getCvDag = MainLowLidIDList.getDagPath(1)
                MFn_mesh = api.MFnMesh(getPolyDag)
                MIt_mesh = api.MItMeshFaceVertex(getPolyDag)
                MFn_NurbsCurve = api.MFnNurbsCurve(getCvDag)

                self.lidMainLowList = []
                cvPositions = [cvMPos for cvMPos in MFn_NurbsCurve.cvPositions(api.MSpace.kObject)]
                for CVPos in cvPositions:
                    Mpoint, faceID = MFn_mesh.getClosestPoint(CVPos, api.MSpace.kObject)
                    faceVtxCount = MFn_mesh.polygonVertexCount(faceID)

                    for s in range(faceVtxCount):
                        MIt_mesh.setIndex(faceID, s)
                        getFaceId = MIt_mesh.vertexId()
                        if MFn_mesh.getPoint(getFaceId) == Mpoint:
                            if getFaceId in self.lidMainUpList:
                                continue
                            self.lidMainLowList.append(getFaceId)

                if 'OtherCrv_grp' in cmds.ls():
                    pass
                elif 'OtherCrv_grp' not in cmds.ls():
                    self.OtherCrvGrp = cmds.group(em=True, n='OtherCrv_grp')
                    cmds.setAttr(self.OtherCrvGrp + '.v', False)
                cmds.parent(self.mainUpCrv, self.OtherCrvGrp)
                cmds.parent(self.mainLowCrv, self.OtherCrvGrp)

                cmds.delete(self.judge_LR + 'lid_crv')
                cmds.select(cl=True)

    def CreateInnerCrv(self, *args):
        if cmds.textFieldGrp(self.names, q=True, tx=True) == '':
            mel.eval("print please_Enter_a_name")
        elif cmds.textFieldGrp(self.names, q=True, tx=True):
            self.name = cmds.textFieldGrp(self.names, q=True, tx=True)
            self.innerUpCrv = self.judge_LR + self.name + 'InnerLidUp_crv'
            self.innerLowCrv = self.judge_LR + self.name + 'InnerLidLow_crv'
            if cmds.ls(sl=True) == []:
                mel.eval("print please_Select_Edge")
            else:
                selEdge = cmds.ls(sl=True, fl=True)
                cmds.polyToCurve(form=2, degree=1, conformToSmoothMeshPreview=False, n=self.judge_LR + 'lid_crv',
                                 ch=False)
                msel = api.MSelectionList()
                msel.add(self.judge_LR + 'lid_crv')
                dagPath = msel.getDagPath(0)
                MFn_Crv = api.MFnNurbsCurve(dagPath)

                getPoss = MFn_Crv.cvPositions(api.MSpace.kWorld)
                posList = [x for x in getPoss]
                MinoutCornerX = min([x[0] for x in getPoss])
                MaxoutCornerX = max([x[0] for x in getPoss])
                for outPos in posList:
                    if outPos[0] == MinoutCornerX and outPos[0] > 0:
                        outCornerVtx_Pos = outPos

                    elif outPos[0] == MaxoutCornerX and outPos[0] < 0:
                        outCornerVtx_Pos = outPos

                toler = MFn_Crv.distanceToPoint(outCornerVtx_Pos, api.MSpace.kObject)
                getDir = MFn_Crv.getParamAtPoint(outCornerVtx_Pos, toler, api.MSpace.kObject)
                cmds.select(self.judge_LR + 'lid_crv.u[%s]' % getDir, r=True)
                mel.eval("moveNurbsCurveSeam")

                getSpans = cmds.getAttr(self.judge_LR + 'lid_crvShape.spans')
                if MFn_Crv.cvPosition(1, api.MSpace.kObject).y < MFn_Crv.cvPosition(getSpans, api.MSpace.kObject).y:
                    cmds.reverseCurve(self.judge_LR + 'lid_crv', ch=False, rpo=1)
                upLipCvPos = []
                upLipCvK = []
                for posIn in range(0, (int(getSpans / 2) + 1)):
                    upLipCvPos.append(cmds.pointPosition(self.judge_LR + 'lid_crv.cv[%s]' % posIn, w=True))
                    upLipCvK.append(posIn)
                cmds.curve(d=1, p=upLipCvPos, k=upLipCvK, n=self.judge_LR + self.name + 'InnerLidUp_crv')
                cmds.rename(cmds.listRelatives(self.judge_LR + self.name + 'InnerLidUp_crv'),
                            self.judge_LR + self.name + 'InnerLidUp_crvShape')
                self.innerUpCrv = self.judge_LR + self.name + 'InnerLidUp_crv'
                cmds.setAttr(self.judge_LR + self.name + 'InnerLidUp_crvShape.dispCV', True)

                InnerUpLidIDList = api.MSelectionList()
                InnerUpLidIDList.add(self.polyObject)
                InnerUpLidIDList.add(self.judge_LR + self.name + 'InnerLidUp_crv')
                getPolyDag = InnerUpLidIDList.getDagPath(0)
                getCvDag = InnerUpLidIDList.getDagPath(1)
                MFn_mesh = api.MFnMesh(getPolyDag)
                MIt_mesh = api.MItMeshFaceVertex(getPolyDag)
                MFn_NurbsCurve = api.MFnNurbsCurve(getCvDag)

                self.lidInnerUpList = []
                cvPositions = [cvMPos for cvMPos in MFn_NurbsCurve.cvPositions(api.MSpace.kObject)]
                for CVPos in cvPositions:
                    Mpoint, faceID = MFn_mesh.getClosestPoint(CVPos, api.MSpace.kObject)
                    faceVtxCount = MFn_mesh.polygonVertexCount(faceID)

                    for s in range(faceVtxCount):
                        MIt_mesh.setIndex(faceID, s)
                        getFaceId = MIt_mesh.vertexId()
                        if MFn_mesh.getPoint(getFaceId) == Mpoint:
                            self.lidInnerUpList.append(getFaceId)

                getSpans = cmds.getAttr(self.judge_LR + 'lid_crvShape.spans')
                if MFn_Crv.cvPosition(1, api.MSpace.kObject).y > MFn_Crv.cvPosition(getSpans, api.MSpace.kObject).y:
                    cmds.reverseCurve(self.judge_LR + 'lid_crv', ch=False, rpo=1)
                lowLipCvPos = []
                lowLipCvK = []
                for posIn in range(0, (int(getSpans / 2) + 1)):
                    lowLipCvPos.append(cmds.pointPosition(self.judge_LR + 'lid_crv.cv[%s]' % posIn, w=True))
                    lowLipCvK.append(posIn)
                cmds.curve(d=1, p=lowLipCvPos, k=lowLipCvK, n=self.judge_LR + self.name + 'InnerLidLow_crv')
                cmds.rename(cmds.listRelatives(self.judge_LR + self.name + 'InnerLidLow_crv'),
                            self.judge_LR + self.name + 'InnerLidLow_crvShape')
                self.innerLowCrv = self.judge_LR + self.name + 'InnerLidLow_crv'
                cmds.setAttr(self.judge_LR + self.name + 'InnerLidLow_crvShape.dispCV', True)

                InnerLowLidIDList = api.MSelectionList()
                InnerLowLidIDList.add(self.polyObject)
                InnerLowLidIDList.add(self.judge_LR + self.name + 'InnerLidLow_crv')
                getPolyDag = InnerLowLidIDList.getDagPath(0)
                getCvDag = InnerLowLidIDList.getDagPath(1)
                MFn_mesh = api.MFnMesh(getPolyDag)
                MIt_mesh = api.MItMeshFaceVertex(getPolyDag)
                MFn_NurbsCurve = api.MFnNurbsCurve(getCvDag)

                self.lidInnerLowList = []
                cvPositions = [cvMPos for cvMPos in MFn_NurbsCurve.cvPositions(api.MSpace.kObject)]
                for CVPos in cvPositions:
                    Mpoint, faceID = MFn_mesh.getClosestPoint(CVPos, api.MSpace.kObject)
                    faceVtxCount = MFn_mesh.polygonVertexCount(faceID)

                    for s in range(faceVtxCount):
                        MIt_mesh.setIndex(faceID, s)
                        getFaceId = MIt_mesh.vertexId()
                        if MFn_mesh.getPoint(getFaceId) == Mpoint:
                            if getFaceId in self.lidInnerUpList:
                                continue
                            self.lidInnerLowList.append(getFaceId)

                if 'OtherCrv_grp' in cmds.ls():
                    pass
                elif 'OtherCrv_grp' not in cmds.ls():
                    self.OtherCrvGrp = cmds.group(em=True, n='OtherCrv_grp')
                cmds.parent(self.innerUpCrv, self.OtherCrvGrp)
                cmds.parent(self.innerLowCrv, self.OtherCrvGrp)

                cmds.delete(self.judge_LR + 'lid_crv')
                cmds.select(cl=True)

    def createSpaceJnts(self, *args):
        if cmds.checkBoxGrp(self.mirrorChesk, q=True, v1=True) == False:
            if cmds.textFieldGrp(self.names, q=True, tx=True) == '':
                mel.eval("print please_Enter_a_name")
            elif cmds.textFieldGrp(self.names, q=True, tx=True):
                self.name = cmds.textFieldGrp(self.names, q=True, tx=True)
                self.innerUpCrv = self.judge_LR + self.name + 'InnerLidUp_crv'
                self.innerLowCrv = self.judge_LR + self.name + 'InnerLidLow_crv'
                if not self.judge_LR + self.name + 'MainLidUp_crv' in cmds.ls():
                    mel.eval("print No_curve_found")
                else:
                    self.lidOtherGrp = cmds.group(em=True, n=self.judge_LR + '%s_Other_grp' % self.name)

                    self.lidUpPathCv = cmds.rebuildCurve(self.judge_LR + self.name + 'MainLidUp_crv', ch=False, rpo=0,
                                                         rt=0, end=1,
                                                         kr=0, kcp=0, kep=1,
                                                         kt=0, s=4, d=3, tol=0.01,
                                                         n=self.judge_LR + self.name + 'UpPath_crv')

                    cmds.addAttr('|' + self.lidUpPathCv[0], ln='blink', at='double', min=0, max=1, dv=0)
                    cmds.setAttr('|' + self.lidUpPathCv[0] + '.blink', e=True, keyable=True)

                    cmds.addAttr('|' + self.lidUpPathCv[0], ln='blinkSize', at='double', min=0, max=1, dv=0.3)
                    cmds.setAttr('|' + self.lidUpPathCv[0] + '.blinkSize', e=True, keyable=True)

                    lidLowPathCv = cmds.rebuildCurve(self.judge_LR + self.name + 'MainLidLow_crv', ch=False, rpo=0,
                                                     rt=0, end=1,
                                                     kr=0, kcp=0, kep=1,
                                                     kt=0, s=4, d=3, tol=0.01,
                                                     n=self.judge_LR + self.name + 'LowPath_crv')

                    self.upLidCrvPointList = [self.judge_LR + self.name + 'InCornerSpace_jnt', '',
                                         self.judge_LR + self.name + 'InUpSpace_jnt',
                                         self.judge_LR + self.name + 'MidUpSpace_jnt',
                                         self.judge_LR + self.name + 'OutUpSpace_jnt', '',
                                         self.judge_LR + self.name + 'OutCornerSpace_jnt']
                    self.LowLidCrvPointList = ['', '', self.judge_LR + self.name + 'InLowSpace_jnt',
                                          self.judge_LR + self.name + 'MidLowSpace_jnt',
                                          self.judge_LR + self.name + 'OutLowSpace_jnt', '',
                                          '']

                    cmds.parent(self.lidUpPathCv, lidLowPathCv, self.lidOtherGrp)

                    sortUpSkinCrvJnts = []
                    sortLowSkinCrvJnts = []

                    eyeLidSpaceJntsGrp = cmds.group(em=True, n=self.judge_LR + self.name + 'SpaceJntsGrp')

                    if self.judge_LR == 'r_':
                        UpVec = (0, 1, 0)
                        aimVec = (0, 0, -1)
                        OrgUpVec = (0, -1, 0)
                        OrgLowVec = (0, 1, 0)

                    if self.judge_LR == 'l_':
                        UpVec = (0, -1, 0)
                        aimVec = (0, 0, 1)
                        OrgUpVec = (0, 1, 0)
                        OrgLowVec = (0, -1, 0)

                    for i, s in enumerate(self.upLidCrvPointList):
                        if i == 1 or i == 5:
                            continue
                        cmds.select(cl=True)
                        lidUpSpaceJnt = cmds.joint(
                            p=cmds.pointPosition(self.judge_LR + self.name + 'UpPath_crv.cv[%s]' % i), n=s)
                        cmds.setAttr(lidUpSpaceJnt + '.drawStyle', 2)
                        lidUpEndJnt = cmds.joint(
                            p=cmds.pointPosition(self.judge_LR + self.name + 'UpPath_crv.cv[%s]' % i),
                            n=s.replace('Space', 'End'))
                        sortUpSkinCrvJnts.append(lidUpEndJnt)
                        if self.judge_LR == 'l_':
                            cmds.setAttr(lidUpSpaceJnt + '.jointOrientX', 0)
                            cmds.setAttr(lidUpSpaceJnt + '.jointOrientY', 0)
                        elif self.judge_LR == 'r_':
                            cmds.setAttr(lidUpSpaceJnt + '.jointOrientX', 180)
                            cmds.setAttr(lidUpSpaceJnt + '.jointOrientY', 0)

                    for i, s in enumerate(self.LowLidCrvPointList):
                        if i == 0 or i == 1 or i == 5 or i == 6:
                            continue
                        cmds.select(cl=True)
                        lidLowSpaceJnt = cmds.joint(
                            p=cmds.pointPosition(self.judge_LR + self.name + 'LowPath_crv.cv[%s]' % i), n=s)
                        cmds.setAttr(lidLowSpaceJnt + '.drawStyle', 2)
                        lidLowEndJnt = cmds.joint(
                            p=cmds.pointPosition(self.judge_LR + self.name + 'LowPath_crv.cv[%s]' % i),
                            n=s.replace('Space', 'End'))
                        if self.judge_LR == 'l_':
                            cmds.setAttr(lidLowSpaceJnt + '.jointOrientX', 180)
                            cmds.setAttr(lidLowSpaceJnt + '.jointOrientY', 180)
                        elif self.judge_LR == 'r_':
                            cmds.setAttr(lidLowSpaceJnt + '.jointOrientX', 0)
                            cmds.setAttr(lidLowSpaceJnt + '.jointOrientY', 180)
                        sortLowSkinCrvJnts.append(lidLowEndJnt)

                    for i, s in enumerate(self.upLidCrvPointList):
                        if i == 1 or i == 5:
                            continue
                        cmds.select(cl=True)
                        if i == 0:
                            self.lidUpIcRootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))

                            cmds.delete(
                                cmds.aimConstraint(s, self.lidUpIcRootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.upLidCrvPointList[-1]))
                            cmds.makeIdentity(self.lidUpIcRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.upLidCrvPointList[i], self.lidUpIcRootJnt)
                            cmds.parent(self.lidUpIcRootJnt, eyeLidSpaceJntsGrp)
                        elif i == 2:
                            lidUpIRootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, lidUpIRootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.LowLidCrvPointList[2]))
                            cmds.makeIdentity(lidUpIRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.upLidCrvPointList[i], lidUpIRootJnt)
                            cmds.parent(lidUpIRootJnt, eyeLidSpaceJntsGrp)
                        elif i == 3:
                            self.lidUpMRootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, self.lidUpMRootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.LowLidCrvPointList[3]))
                            cmds.makeIdentity(self.lidUpMRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.upLidCrvPointList[i], self.lidUpMRootJnt)
                            cmds.parent(self.lidUpMRootJnt, eyeLidSpaceJntsGrp)
                        elif i == 4:
                            self.lidUpORootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, self.lidUpORootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.LowLidCrvPointList[4]))
                            cmds.makeIdentity(self.lidUpORootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.upLidCrvPointList[i], self.lidUpORootJnt)
                            cmds.parent(self.lidUpORootJnt, eyeLidSpaceJntsGrp)
                        elif i == 6:
                            self.lidUpOCRootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, self.lidUpOCRootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.upLidCrvPointList[0]))
                            cmds.makeIdentity(self.lidUpOCRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.upLidCrvPointList[i], self.lidUpOCRootJnt)
                            cmds.parent(self.lidUpOCRootJnt, eyeLidSpaceJntsGrp)

                    for i, s in enumerate(self.LowLidCrvPointList):
                        if i == 0 or i == 1 or i == 5 or i == 6:
                            continue
                        cmds.select(cl=True)
                        if i == 2:
                            lidLowIRootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, lidLowIRootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.upLidCrvPointList[2]))
                            cmds.makeIdentity(lidLowIRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.LowLidCrvPointList[i], lidLowIRootJnt)
                            cmds.parent(lidLowIRootJnt, eyeLidSpaceJntsGrp)
                        elif i == 3:
                            self.lidLowMRootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, self.lidLowMRootJnt, offset=(0, 0, 0), weight=1,
                                                   aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.upLidCrvPointList[3]))
                            cmds.makeIdentity(self.lidLowMRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.LowLidCrvPointList[i], self.lidLowMRootJnt)
                            cmds.parent(self.lidLowMRootJnt, eyeLidSpaceJntsGrp)
                        elif i == 4:
                            self.lidLowORootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, self.lidLowORootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.upLidCrvPointList[4]))
                            cmds.makeIdentity(self.lidLowORootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.LowLidCrvPointList[i], self.lidLowORootJnt)
                            cmds.parent(self.lidLowORootJnt, eyeLidSpaceJntsGrp)

                cmds.skinCluster(sortUpSkinCrvJnts, self.judge_LR + self.name + 'UpPath_crv', tsb=True,
                                 n=self.judge_LR + self.name + 'UpCrv_sct')
                cmds.skinPercent(self.judge_LR + self.name + 'UpCrv_sct',
                                 self.judge_LR + self.name + 'UpPath_crv.cv[1]',
                                 transformValue=[(sortUpSkinCrvJnts[0], 0.6), (sortUpSkinCrvJnts[1], 0.4)])
                cmds.skinPercent(self.judge_LR + self.name + 'UpCrv_sct',
                                 self.judge_LR + self.name + 'UpPath_crv.cv[5]',
                                 transformValue=[(sortUpSkinCrvJnts[3], 0.4), (sortUpSkinCrvJnts[4], 0.6)])

                cmds.skinCluster(sortUpSkinCrvJnts[0], sortLowSkinCrvJnts, sortUpSkinCrvJnts[4],
                                 self.judge_LR + self.name + 'LowPath_crv', tsb=True,
                                 n=self.judge_LR + self.name + 'LowCrv_sct')
                cmds.skinPercent(self.judge_LR + self.name + 'LowCrv_sct',
                                 self.judge_LR + self.name + 'LowPath_crv.cv[1]',
                                 transformValue=[(sortUpSkinCrvJnts[0], 0.6), (sortLowSkinCrvJnts[0], 0.4)])
                cmds.skinPercent(self.judge_LR + self.name + 'LowCrv_sct',
                                 self.judge_LR + self.name + 'LowPath_crv.cv[5]',
                                 transformValue=[(sortUpSkinCrvJnts[4], 0.6), (sortLowSkinCrvJnts[2], 0.4)])

                MlidUpCrvList = api.MSelectionList()
                MlidUpCrvList.add(self.judge_LR + self.name + 'MainLidUp_crv')
                MlidUpCrvList.add(self.judge_LR + self.name + 'UpPath_crv')
                MlidUpCrvDag = MlidUpCrvList.getDagPath(0)
                MlidUpPathDag = MlidUpCrvList.getDagPath(1)
                MFn_lipUpCrv = api.MFnNurbsCurve(MlidUpCrvDag)
                MFn_lipUpPathCrv = api.MFnNurbsCurve(MlidUpPathDag)
                lidUpCvPosList = [index for index in MFn_lipUpCrv.cvPositions()]
                lidUpAimLocsGrp = cmds.group(em=True, n=self.judge_LR + self.name + 'UpAimLocs_grp')
                cmds.setAttr(lidUpAimLocsGrp + '.v', False)
                cmds.parent(lidUpAimLocsGrp, self.lidOtherGrp)
                getArclen = (cmds.arclen(self.judge_LR + self.name + 'UpPath_crv') * 0.001)

                lidUpTargetLocList = []
                for i, Mpoints in enumerate(lidUpCvPosList):
                    getLidUpCrvdisToPoint = MFn_lipUpPathCrv.distanceToPoint(Mpoints, api.MSpace.kObject)
                    getUpCrvParam = MFn_lipUpPathCrv.getParamAtPoint(Mpoints, getLidUpCrvdisToPoint + getArclen,
                                                                     api.MSpace.kObject)
                    aimUpLoc = cmds.spaceLocator(n=self.judge_LR + self.name + 'Aim%sUp_loc' % i)
                    lidUpTargetLocList.append(aimUpLoc[0])
                    cmds.setAttr(cmds.listRelatives(aimUpLoc[0])[0] + '.localScale', 0.01, 0.01, 0.01)
                    aimUpGrp = cmds.group(aimUpLoc, n=self.judge_LR + self.name + 'Aim%sUpLoc_grp' % i)
                    lidUpPci = cmds.createNode('pointOnCurveInfo', n=self.judge_LR + self.name + 'Aim%s_pci' % i)

                    cmds.connectAttr(cmds.listRelatives(self.judge_LR + self.name + 'UpPath_crv')[0] + '.worldSpace[0]',
                                     lidUpPci + '.inputCurve')
                    cmds.setAttr(lidUpPci + '.parameter', getUpCrvParam)
                    cmds.connectAttr(lidUpPci + '.positionX', aimUpGrp + '.translateX')
                    cmds.connectAttr(lidUpPci + '.positionY', aimUpGrp + '.translateY')
                    cmds.connectAttr(lidUpPci + '.positionZ', aimUpGrp + '.translateZ')
                    cmds.parent(aimUpGrp, lidUpAimLocsGrp)
                MlidLowCrvList = api.MSelectionList()
                MlidLowCrvList.add(self.judge_LR + self.name + 'MainLidLow_crv')
                MlidLowCrvList.add(self.judge_LR + self.name + 'LowPath_crv')
                MlidLowCrvDag = MlidLowCrvList.getDagPath(0)
                MlidLowPathDag = MlidLowCrvList.getDagPath(1)
                MFn_lipLowCrv = api.MFnNurbsCurve(MlidLowCrvDag)
                MFn_lipLowPathCrv = api.MFnNurbsCurve(MlidLowPathDag)
                lidLowCvPosList = [index for index in MFn_lipLowCrv.cvPositions()]
                lidLowAimLocsGrp = cmds.group(em=True, n=self.judge_LR + self.name + 'LowAimLocs_grp')
                cmds.setAttr(lidLowAimLocsGrp + '.v', False)
                cmds.parent(lidLowAimLocsGrp, self.lidOtherGrp)

                lidLowTargetLocList = []
                for i, Mpoints in enumerate(lidLowCvPosList):
                    if i == 0 or i == len(lidLowCvPosList) - 1:
                        continue
                    getLidLowCrvdisToPoint = MFn_lipLowPathCrv.distanceToPoint(Mpoints, api.MSpace.kObject)
                    getLowCrvParam = MFn_lipLowPathCrv.getParamAtPoint(Mpoints, getLidLowCrvdisToPoint + getArclen,
                                                                       api.MSpace.kObject)
                    aimLowLoc = cmds.spaceLocator(n=self.judge_LR + self.name + 'Aim%sLow_loc' % i)
                    lidLowTargetLocList.append(aimLowLoc[0])
                    cmds.setAttr(cmds.listRelatives(aimLowLoc[0])[0] + '.localScale', 0.01, 0.01, 0.01)
                    aimLowGrp = cmds.group(aimLowLoc, n=self.judge_LR + self.name + 'Aim%sLowLoc_grp' % i)
                    lidLowPci = cmds.createNode('pointOnCurveInfo', n=self.judge_LR + self.name + 'Aim%s_pci' % i)

                    cmds.connectAttr(
                        cmds.listRelatives(self.judge_LR + self.name + 'LowPath_crv')[0] + '.worldSpace[0]',
                        lidLowPci + '.inputCurve')
                    cmds.setAttr(lidLowPci + '.parameter', getLowCrvParam)
                    cmds.connectAttr(lidLowPci + '.positionX', aimLowGrp + '.translateX')
                    cmds.connectAttr(lidLowPci + '.positionY', aimLowGrp + '.translateY')
                    cmds.connectAttr(lidLowPci + '.positionZ', aimLowGrp + '.translateZ')
                    cmds.parent(aimLowGrp, lidLowAimLocsGrp)

                cmds.delete(self.OtherCrvGrp)
                cmds.select(cl=True)

                lidOrgGrp = cmds.group(em=True, n=self.judge_LR + '%sOrgJnts_grp' % self.name)
                cmds.setAttr(lidOrgGrp + '.v', False)
                lidSkinJntsGrp = cmds.group(em=True, n=self.judge_LR + '%sSkinJnts_grp' % self.name)
                cmds.setAttr(lidSkinJntsGrp + '.v', False)

                lidUpOrgList = []
                lidLowOrgList = []

                lidUpSkinJntsList = []
                lidLowSkinJntsList = []

                lidUpSkinEndJntsList = []
                lidLowSkinEndJntsList = []

                for i, aimLocIndex in enumerate(lidUpTargetLocList):
                    if i == 0 or i == len(lidUpTargetLocList) - 1:
                        continue
                    cmds.select(cl=True)
                    lidUpOrgJnt = cmds.joint(n=aimLocIndex.replace('_loc', 'Org_jnt'),
                                             p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True))
                    lidUpOrgList.append(lidUpOrgJnt)
                    cmds.select(cl=True)
                    lidUpOrgEndJnt = cmds.joint(n=aimLocIndex.replace('_loc', 'OrgEnd_jnt'),
                                                p=cmds.xform(aimLocIndex, q=True, ws=True, t=True))
                    cmds.select(cl=True)
                    lidUpSkinRootJnt = cmds.joint(
                        n=self.judge_LR + '%sUpLidSkinRoot%s_jnt' % (self.name, str(i).zfill(2)),
                        p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True))
                    cmds.setAttr(lidUpSkinRootJnt + '.drawStyle', 2)

                    cmds.select(cl=True)
                    lidUpSkinEndJnt = cmds.joint(
                        n=self.judge_LR + '%sUpLidSkinEnd%s_jnt' % (self.name, str(i).zfill(2)),
                        p=cmds.xform(aimLocIndex, q=True, ws=True, t=True))
                    lidUpSkinEndJntsList.append(lidUpSkinEndJnt)
                    cmds.setAttr(lidUpSkinEndJnt + '.radius', 0.1)

                    lidUpSkinJntsList.append(lidUpSkinRootJnt)
                    cmds.delete(
                        cmds.aimConstraint(aimLocIndex, lidUpOrgJnt, offset=(0, 0, 0), weight=1, aimVector=(1, 0, 0),
                                           upVector=OrgLowVec,
                                           worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                           worldUpObject=(self.lidUpMRootJnt)))
                    cmds.makeIdentity(lidUpOrgJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                    cmds.parent(lidUpOrgEndJnt, lidUpOrgJnt)
                    cmds.aimConstraint(aimLocIndex, lidUpOrgJnt, offset=(0, 0, 0), weight=1, aimVector=(1, 0, 0),
                                       upVector=OrgLowVec,
                                       worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                       worldUpObject=(self.lidUpMRootJnt), n=lidUpOrgJnt.replace('_jnt', '_aim'))
                    cmds.parent(lidUpOrgJnt, lidOrgGrp)

                    cmds.setAttr(lidUpSkinEndJnt + '.jointOrient', 0, 0, 0)
                    cmds.setAttr(lidUpSkinRootJnt + '.jointOrient', cmds.getAttr(lidUpOrgJnt + '.jointOrientX'),
                                 cmds.getAttr(lidUpOrgJnt + '.jointOrientY'),
                                 cmds.getAttr(lidUpOrgJnt + '.jointOrientZ'))
                    cmds.parent(lidUpSkinEndJnt, lidUpSkinRootJnt)
                    cmds.parent(lidUpSkinRootJnt, lidSkinJntsGrp)

                for i, aimLocIndex in enumerate(lidLowTargetLocList):
                    cmds.select(cl=True)
                    lidLowOrgJnt = cmds.joint(n=aimLocIndex.replace('_loc', 'Org_jnt'),
                                              p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True))
                    lidLowOrgList.append(lidLowOrgJnt)
                    cmds.select(cl=True)
                    lidLowOrgEndJnt = cmds.joint(n=aimLocIndex.replace('_loc', 'OrgEnd_jnt'),
                                                 p=cmds.xform(aimLocIndex, q=True, ws=True, t=True))

                    cmds.select(cl=True)
                    lidLowSkinRootJnt = cmds.joint(
                        n=self.judge_LR + '%sLowLidSkinRoot%s_jnt' % (self.name, str(i + 1).zfill(2)),
                        p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True))
                    cmds.setAttr(lidLowSkinRootJnt + '.drawStyle', 2)

                    cmds.select(cl=True)
                    lidLowSkinEndJnt = cmds.joint(
                        n=self.judge_LR + '%sLowLidSkinEnd%s_jnt' % (self.name, str(i + 1).zfill(2)),
                        p=cmds.xform(aimLocIndex, q=True, ws=True, t=True))
                    cmds.setAttr(lidLowSkinEndJnt + '.radius', 0.1)

                    lidLowSkinEndJntsList.append(lidLowSkinEndJnt)
                    lidLowSkinJntsList.append(lidLowSkinRootJnt)

                    cmds.delete(
                        cmds.aimConstraint(aimLocIndex, lidLowOrgJnt, offset=(0, 0, 0), weight=1, aimVector=(1, 0, 0),
                                           upVector=OrgUpVec,
                                           worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                           worldUpObject=(self.lidLowMRootJnt)))
                    cmds.makeIdentity(lidLowOrgJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                    cmds.parent(lidLowOrgEndJnt, lidLowOrgJnt)
                    cmds.aimConstraint(aimLocIndex, lidLowOrgJnt, offset=(0, 0, 0), weight=1, aimVector=(1, 0, 0),
                                       upVector=OrgUpVec,
                                       worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                       worldUpObject=(self.lidLowMRootJnt), n=lidLowOrgJnt.replace('_jnt', '_aim'))
                    cmds.parent(lidLowOrgJnt, lidOrgGrp)

                    cmds.setAttr(lidLowSkinEndJnt + '.jointOrient', 0, 0, 0)
                    cmds.setAttr(lidLowSkinRootJnt + '.jointOrient', cmds.getAttr(lidLowOrgJnt + '.jointOrientX'),
                                 cmds.getAttr(lidLowOrgJnt + '.jointOrientY'),
                                 cmds.getAttr(lidLowOrgJnt + '.jointOrientZ'))
                    cmds.parent(lidLowSkinEndJnt, lidLowSkinRootJnt)
                    cmds.parent(lidLowSkinRootJnt, lidSkinJntsGrp)

                lidUpOctList = []
                lidLowOctList = []

                for i, lidUpSkinJnts in enumerate(lidUpSkinJntsList):
                    lidUpOct = cmds.orientConstraint(lidUpOrgList[i], lidLowOrgList[i], lidUpSkinJnts,
                                                     offset=(0, 0, 0), weight=1,
                                                     n=self.judge_LR + '%sUpConstructor%s_oct' % (
                                                         self.name, str(i + 1).zfill(2)))
                    cmds.setAttr(lidUpOct[0] + '.interpType', 2)
                    lidUpOctList.append(lidUpOct[0])

                    lidLowOct = cmds.orientConstraint(lidLowOrgList[i], lidUpOrgList[i], lidLowSkinJntsList[i],
                                                      offset=(0, 0, 0),
                                                      weight=1,
                                                      n=self.judge_LR + '%sLowConstructor%s_oct' % (
                                                          self.name, str(i + 1).zfill(2)))
                    cmds.setAttr(lidLowOct[0] + '.interpType', 2)
                    lidLowOctList.append(lidLowOct[0])
                cmds.select(cl=True)

                lidBlinkRvs = cmds.createNode('reverse', n=self.judge_LR + '%slidBlink_rvs' % self.name)
                lidUpSRmv = cmds.createNode('remapValue', n=self.judge_LR + '%sUpLidStart_rmv' % self.name)
                lidUpERmv = cmds.createNode('remapValue', n=self.judge_LR + '%sUpLidEnd_rmv' % self.name)
                lidLowSRmv = cmds.createNode('remapValue', n=self.judge_LR + '%sLowLidStart_rmv' % self.name)
                lidLowERmv = cmds.createNode('remapValue', n=self.judge_LR + '%sLowLidEnd_rmv' % self.name)

                cmds.connectAttr(self.lidUpPathCv[0] + '.blink', lidUpSRmv + '.inputValue')
                cmds.connectAttr(self.lidUpPathCv[0] + '.blinkSize', lidUpSRmv + '.outputMax')
                cmds.connectAttr(self.lidUpPathCv[0] + '.blink', lidUpERmv + '.inputValue')
                cmds.connectAttr(self.lidUpPathCv[0] + '.blinkSize', lidBlinkRvs + '.inputX')
                cmds.connectAttr(lidBlinkRvs + '.outputX', lidUpERmv + '.outputMax')

                cmds.connectAttr(self.lidUpPathCv[0] + '.blink', lidLowSRmv + '.inputValue')
                cmds.connectAttr(lidBlinkRvs + '.outputX', lidLowSRmv + '.outputMax')
                cmds.connectAttr(self.lidUpPathCv[0] + '.blink', lidLowERmv + '.inputValue')
                cmds.connectAttr(self.lidUpPathCv[0] + '.blinkSize', lidLowERmv + '.outputMax')

                cmds.setAttr(lidUpSRmv + '.outputMin', 1)
                cmds.setAttr(lidLowSRmv + '.outputMin', 1)

                for i, indexUpOct in enumerate(lidUpOctList):
                    cmds.connectAttr(lidUpSRmv + '.outValue', indexUpOct + '.' + lidUpOrgList[i] + 'W0')
                    cmds.connectAttr(lidUpERmv + '.outValue', indexUpOct + '.' + lidLowOrgList[i] + 'W1')

                for i, indexLowOct in enumerate(lidLowOctList):
                    cmds.connectAttr(lidLowSRmv + '.outValue', indexLowOct + '.' + lidLowOrgList[i] + 'W0')
                    cmds.connectAttr(lidLowERmv + '.outValue', indexLowOct + '.' + lidUpOrgList[i] + 'W1')

                cmds.select(cl=True)
                lidInCSkinRootJnt = cmds.joint(n=self.judge_LR + '%sUpLidSkinRoot0_jnt' % self.name,
                                               p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True))
                cmds.setAttr(lidInCSkinRootJnt + '.drawStyle', 2)
                cmds.setAttr(lidInCSkinRootJnt + '.jointOrient', cmds.getAttr(self.lidUpIcRootJnt + '.jointOrientX'),
                             cmds.getAttr(self.lidUpIcRootJnt + '.jointOrientY'),
                             cmds.getAttr(self.lidUpIcRootJnt + '.jointOrientZ'))
                cmds.delete(cmds.aimConstraint(lidUpTargetLocList[0], lidInCSkinRootJnt, offset=(0, 0, 0), weight=1,
                                               aimVector=(1, 0, 0),
                                               upVector=(0, 1, 0),
                                               worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                               worldUpObject=(self.lidUpMRootJnt),
                                               n=lidInCSkinRootJnt.replace('_jnt', '_aim')))
                cmds.makeIdentity(lidInCSkinRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)

                cmds.select(cl=True)
                lidInCSkinEndJnt = cmds.joint(n=self.judge_LR + '%sUpLidSkinEnd0_jnt' % self.name,
                                              p=cmds.xform(lidUpTargetLocList[0], q=True, ws=True, t=True))
                cmds.parent(lidInCSkinEndJnt, lidInCSkinRootJnt)
                cmds.setAttr(lidInCSkinEndJnt + '.radius', 0.1)

                cmds.aimConstraint(lidUpTargetLocList[0], lidInCSkinRootJnt, offset=(0, 0, 0), weight=1,
                                   aimVector=(1, 0, 0),
                                   upVector=(0, 1, 0),
                                   worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                   worldUpObject=(self.lidUpMRootJnt), n=lidInCSkinRootJnt.replace('_jnt', '_aim'))

                cmds.select(cl=True)
                lidOutCSkinRootJnt = cmds.joint(
                    n=self.judge_LR + '%sUpLidSkinRoot%s_jnt' % (self.name, len(lidUpTargetLocList) - 1),
                    p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True))
                cmds.setAttr(lidOutCSkinRootJnt + '.drawStyle', 2)

                cmds.delete(cmds.aimConstraint(lidUpTargetLocList[-1], lidOutCSkinRootJnt, offset=(0, 0, 0), weight=1,
                                               aimVector=(1, 0, 0),
                                               upVector=(0, 1, 0),
                                               worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                               worldUpObject=(self.lidUpMRootJnt),
                                               n=lidOutCSkinRootJnt.replace('_jnt', '_aim')))
                cmds.makeIdentity(lidOutCSkinRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)

                cmds.select(cl=True)
                lidOutCSkinEndJnt = cmds.joint(
                    n=self.judge_LR + '%sUpLidSkinEnd%s_jnt' % (self.name, len(lidUpTargetLocList) - 1),
                    p=cmds.xform(lidUpTargetLocList[-1], q=True, ws=True, t=True))

                cmds.parent(lidOutCSkinEndJnt, lidOutCSkinRootJnt)
                cmds.setAttr(lidOutCSkinEndJnt + '.radius', 0.1)

                cmds.aimConstraint(lidUpTargetLocList[-1], lidOutCSkinRootJnt, offset=(0, 0, 0), weight=1,
                                   aimVector=(1, 0, 0),
                                   upVector=(0, 1, 0),
                                   worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                   worldUpObject=(self.lidUpMRootJnt),
                                   n=lidOutCSkinRootJnt.replace('_jnt', '_aim'))

                cmds.parent(lidInCSkinRootJnt, lidOutCSkinRootJnt, lidSkinJntsGrp)

                lidUpSkinEndJntsList.insert(0, lidInCSkinEndJnt)
                lidUpSkinEndJntsList.insert(len(lidUpSkinEndJntsList), lidOutCSkinEndJnt)

                lidUpSkinJntsList.insert(0, lidInCSkinRootJnt)
                lidUpSkinJntsList.insert(len(lidUpSkinJntsList), lidOutCSkinRootJnt)

                # skinVtxList -------------------------------------------------

                msel = api.MSelectionList()
                msel.add(self.polyObject)
                dag = msel.getDagPath(0)
                MFn_mesh = api.MFnMesh(dag)
                MIt_mesh = api.MItMeshVertex(dag)

                self.lidUpSortVtxIdList = []
                for i, index in enumerate(self.lidInnerUpList):
                    oldVtxList = []
                    cmds.select(self.polyObject + '.vtx[%s]' % index,
                                self.polyObject + '.vtx[%s]' % self.lidOuterUpList[i], r=True)
                    cmds.SelectEdgeLoopSp()
                    oldSel = cmds.ls(sl=True, fl=True)
                    for oldIn in oldSel:
                        cmds.select(oldIn, r=True)
                        Mglobal = api.MGlobal.getRichSelection()
                        richSel = api.MRichSelection(Mglobal)
                        getSelection = richSel.getSelection()
                        getComponent = getSelection.getComponent(0)
                        MFnSingle = api.MFnSingleIndexedComponent(getComponent[1])
                        elenemt = MFnSingle.getElements()
                        oldVtxList.append(elenemt[0])

                    sortVtxID = []
                    for i2 in range(len(oldVtxList)):
                        if i2 == 0:
                            sortVtxID.append(self.lidInnerUpList[i])
                            MIt_mesh.setIndex(self.lidInnerUpList[i])
                            continue
                        getSkinVtxList = MIt_mesh.getConnectedVertices()
                        for getIn2 in getSkinVtxList:
                            if getIn2 in oldVtxList and not getIn2 in sortVtxID:
                                sortVtxID.append(getIn2)
                                MIt_mesh.setIndex(getIn2)
                    self.lidUpSortVtxIdList.append(sortVtxID)

                self.lidLowSortVtxIdList = []
                for i, index in enumerate(self.lidInnerLowList):
                    oldVtxList = []
                    cmds.select(self.polyObject + '.vtx[%s]' % index,
                                self.polyObject + '.vtx[%s]' % self.lidOuterLowList[i], r=True)
                    cmds.SelectEdgeLoopSp()
                    oldSel = cmds.ls(sl=True, fl=True)
                    for oldIn in oldSel:
                        cmds.select(oldIn, r=True)
                        Mglobal = api.MGlobal.getRichSelection()
                        richSel = api.MRichSelection(Mglobal)
                        getSelection = richSel.getSelection()
                        getComponent = getSelection.getComponent(0)
                        MFnSingle = api.MFnSingleIndexedComponent(getComponent[1])
                        elenemt = MFnSingle.getElements()
                        oldVtxList.append(elenemt[0])

                    sortVtxID = []
                    for i2 in range(len(oldVtxList)):
                        if i2 == 0:
                            sortVtxID.append(self.lidInnerLowList[i])
                            MIt_mesh.setIndex(self.lidInnerLowList[i])
                            continue
                        getSkinVtxList = MIt_mesh.getConnectedVertices()
                        for getIn2 in getSkinVtxList:
                            if getIn2 in oldVtxList and not getIn2 in sortVtxID:
                                sortVtxID.append(getIn2)
                                MIt_mesh.setIndex(getIn2)
                    self.lidLowSortVtxIdList.append(sortVtxID)
                cmds.select(cl=True)

                lidUpPoint = api.MPoint(cmds.xform(self.upLidCrvPointList[3], q=True, ws=True, t=True))
                lidLowPoint = api.MPoint(cmds.xform(self.LowLidCrvPointList[3], q=True, ws=True, t=True))
                distance = lidUpPoint.distanceTo(lidLowPoint)
                alignList = ['In', 'Mid', 'Out']
                XYZList = ['X', 'Y', 'Z']
                RGBList = ['R', 'G', 'B']
                ctlsSize = (cmds.getAttr(self.upLidCrvPointList[3]+'.tz') * 0.2)

                if self.judge_LR == 'l_':
                    tzOffset = ctlsSize / 2

                    lidUpRoot_ctl = cmds.circle(c=(0, 0, tzOffset), nr=(0, 0, 1), sw=360, r=ctlsSize,
                                                d=3, ut=0, tol=0.01, s=8, ch=False,
                                                n=self.judge_LR + self.name + 'UpRoot_ctl')
                    lidUpRootCtlGrp = cmds.group(lidUpRoot_ctl, n=self.judge_LR + self.name + 'UpRootCtl_grp')
                    for Cvs in range(4, 7):
                        cmds.xform(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, ws=True, t=(
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[0], 4),
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[3]', w=True)[1], 4),
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[2], 4)
                        ))
                    cmds.xform(lidUpRootCtlGrp, ws=True,
                               t=cmds.xform(self.upLidCrvPointList[3], q=True, ws=True, t=True))
                    cmds.transformLimits(lidUpRoot_ctl[0], ty=(-1, 1), ety=(0, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], ty=(-1, 1), ety=(1, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], tz=(-1, 1), etx=(0, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], tz=(-1, 1), etx=(1, 1))
                    cmds.setAttr(lidUpRootCtlGrp + '.s', distance, distance, distance)

                    lidUpTYMdi = cmds.createNode('multiplyDivide', n=self.judge_LR+self.name+'UpTY_mdi')
                    lidUpTYPma = cmds.createNode('plusMinusAverage', n=self.judge_LR+self.name+'UpTY_pma')
                    lidUpTXPma = cmds.createNode('plusMinusAverage', n=self.judge_LR+self.name+'UpTX_pma')
                    lidUpRZ45Mdi = cmds.createNode('multiplyDivide', n=self.judge_LR+self.name+'Up45RZ_mdi')
                    cmds.setAttr(lidUpRZ45Mdi + '.input2X', -45)
                    cmds.setAttr(lidUpRZ45Mdi + '.input2Z', 45)
                    cmds.setAttr(lidUpRZ45Mdi + '.operation', 2)
                    lidUpRZMdi = cmds.createNode('multiplyDivide', n=self.judge_LR+self.name+'UpRZ_mdi')
                    lidUpTXMdi = cmds.createNode('multiplyDivide', n=self.judge_LR+self.name+'UpTX_mdi')
                    cmds.setAttr(lidUpTXMdi + '.input2X', 10)
                    cmds.setAttr(lidUpTXMdi + '.input2Y', 20)

                    for i, AL in enumerate(alignList):
                        cmds.setAttr(lidUpTYMdi + '.input2%s' % XYZList[i],
                                     cmds.getAttr(self.judge_LR+self.name+'%sUpRoot_jnt.jointOrientX' % AL) + cmds.getAttr(
                                         self.judge_LR+self.name+'%sLowRoot_jnt.jointOrientX' % AL))
                        cmds.connectAttr(lidUpRoot_ctl[0] + '.translateY', lidUpTYMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpTYMdi + '.output%s' % XYZList[i],
                                         lidUpTYPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTYPma + '.output3D%s' % XYZList[i].lower(),
                                         self.judge_LR+self.name+'%sUpRoot_jnt.rotateX' % AL)

                        if i == 1:
                            cmds.connectAttr(lidUpTXMdi + '.outputY',
                                             lidUpTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                            cmds.connectAttr(lidUpTXPma + '.output3D%s' % XYZList[i].lower(),
                                             self.judge_LR+self.name+'%sUpRoot_jnt.rotateY' % AL)
                            continue
                        cmds.setAttr(lidUpRZMdi + '.input2%s' % XYZList[i],
                                     cmds.getAttr(self.judge_LR+self.name+'%sUpRoot_jnt.jointOrientX' % AL) + cmds.getAttr(
                                         self.judge_LR+self.name+'%sLowRoot_jnt.jointOrientX' % AL))
                        cmds.connectAttr(lidUpRoot_ctl[0] + '.rotateZ', lidUpRZ45Mdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpRZ45Mdi + '.output%s' % XYZList[i], lidUpRZMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpRZMdi + '.output%s' % XYZList[i],
                                         lidUpTYPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTXMdi + '.outputX',
                                         lidUpTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTXPma + '.output3D%s' % XYZList[i].lower(),
                                         self.judge_LR+self.name+'%sUpRoot_jnt.rotateY' % AL)

                    cmds.connectAttr(lidUpRoot_ctl[0] + '.translateX', lidUpTXMdi + '.input1X')
                    cmds.connectAttr(lidUpRoot_ctl[0] + '.translateX', lidUpTXMdi + '.input1Y')

                    lidLowRoot_ctl = cmds.circle(c=(0, 0, tzOffset), nr=(0, 0, 1), sw=360, r=ctlsSize,
                                                 d=3, ut=0, tol=0.01, s=8, ch=False, n=self.judge_LR+self.name+'LowRoot_ctl')
                    lidLowRootCtlGrp = cmds.group(lidLowRoot_ctl, n=self.judge_LR+self.name+'LowRootCtl_grp')
                    for Cvs in range(4, 7):
                        cmds.xform(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, ws=True, t=(
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[0], 4),
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[3]', w=True)[1], 4),
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[2], 4)
                        ))
                    cmds.xform(lidLowRootCtlGrp, ws=True, t=cmds.xform(self.judge_LR+self.name+'MidLowSpace_jnt', q=True, ws=True, t=True))
                    cmds.transformLimits(lidLowRoot_ctl[0], ty=(-1, 1), ety=(0, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], ty=(-1, 1), ety=(1, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], tz=(-1, 1), etx=(0, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], tz=(-1, 1), etx=(1, 1))
                    cmds.setAttr(lidLowRootCtlGrp + '.s', distance, -distance, distance)

                    lidLowTYPma = cmds.createNode('plusMinusAverage', n=self.judge_LR+self.name+'LowTY_pma')
                    lidLowTYRTPma = cmds.createNode('plusMinusAverage', n=self.judge_LR+self.name+'LowTYRT_pma')
                    lidLowRZ45Mdi = cmds.createNode('multiplyDivide', n=self.judge_LR+self.name+'Low45RZ_mdi')
                    cmds.setAttr(lidLowRZ45Mdi + '.input2X', -45)
                    cmds.setAttr(lidLowRZ45Mdi + '.input2Z', 45)
                    cmds.setAttr(lidLowRZ45Mdi + '.operation', 2)
                    lidLowTYMdi = cmds.createNode('multiplyDivide', n=self.judge_LR+self.name+'LowTY_mdi')
                    lidLowTYMinMdi = cmds.createNode('multiplyDivide', n=self.judge_LR+self.name+'LowTYMin_mdi')
                    cmds.setAttr(lidLowTYMinMdi + '.input2', -1, -1, -1)
                    lidLowOutBcl = cmds.createNode('blendColors', n=self.judge_LR+self.name+'LowOut_bcl')
                    cmds.setAttr(lidLowOutBcl + '.blender', 1)

                    upToLowPma = cmds.createNode('plusMinusAverage', n=self.judge_LR+self.name+'UpToLow_pma')
                    cmds.connectAttr(self.judge_LR+self.name+'UpRoot_ctl.translateY', upToLowPma + '.input2D[0].input2Dx')
                    cmds.connectAttr(self.judge_LR+self.name+'UpRoot_ctl.translateY', upToLowPma + '.input2D[0].input2Dy')
                    cmds.connectAttr(lidUpRZ45Mdi + '.outputX', upToLowPma + '.input2D[1].input2Dx')
                    cmds.connectAttr(lidUpRZ45Mdi + '.outputZ', upToLowPma + '.input2D[1].input2Dy')
                    lidUpToLowTYMinMdi = cmds.createNode('multiplyDivide', n=self.judge_LR+self.name+'UpToLowTYMin_mdi')
                    cmds.setAttr(lidUpToLowTYMinMdi + '.input2', -1, -1, -1)
                    cmds.connectAttr(upToLowPma + '.output2Dx', lidUpToLowTYMinMdi + '.input1X')
                    cmds.connectAttr(self.judge_LR+self.name+'UpRoot_ctl.translateY', lidUpToLowTYMinMdi + '.input1Y')
                    cmds.connectAttr(upToLowPma + '.output2Dy', lidUpToLowTYMinMdi + '.input1Z')
                    lidUpToLowRvs = cmds.createNode('reverse', n=self.judge_LR+self.name+'UpToLow_rvs')
                    lidUpToLowTYPlusMdi = cmds.createNode('multiplyDivide', n=self.judge_LR+self.name+'UpToLowTYPlusTY_mdi')
                    lidLowTX = cmds.createNode('multiplyDivide', n=self.judge_LR+self.name+'LowTX_mdi')
                    cmds.setAttr(lidLowTX + '.input2X', -10)
                    cmds.setAttr(lidLowTX + '.input2Y', -20)
                    cmds.connectAttr(lidLowRoot_ctl[0] + '.translateX', lidLowTX + '.input1X')
                    cmds.connectAttr(lidLowRoot_ctl[0] + '.translateX', lidLowTX + '.input1Y')
                    lidLowTXPma = cmds.createNode('plusMinusAverage', n=self.judge_LR+self.name+'LowTX_pma')

                    for i, conIn in enumerate(alignList):
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.translateY',
                                         lidLowTYPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.translateY',
                                         lidLowTYRTPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowTYPma + '.output3D%s' % XYZList[i].lower(),
                                         lidLowTYMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidLowTYRTPma + '.output3D%s' % XYZList[i].lower(),
                                         lidLowTYMinMdi + '.input1%s' % XYZList[i])
                        cmds.setAttr(lidLowTYMdi + '.input2%s' % XYZList[i],
                                     cmds.getAttr(self.judge_LR+self.name+'%sUpRoot_jnt.jointOrientX' % conIn) +
                                     cmds.getAttr(self.judge_LR+self.name+'%sLowRoot_jnt.jointOrientX' % conIn))

                        outCds = cmds.createNode('condition', n=self.judge_LR+self.name+'%sLow_cds' % conIn)
                        cmds.setAttr(outCds + '.operation', 3)
                        cmds.connectAttr(lidLowTYMdi + '.output%s' % XYZList[i], outCds + '.colorIfTrueR')
                        cmds.connectAttr(lidLowTYMinMdi + '.output%s' % XYZList[i], outCds + '.secondTerm')
                        cmds.connectAttr(outCds + '.outColorR', lidLowOutBcl + '.color1%s' % RGBList[i])
                        cmds.connectAttr(lidLowTYMdi + '.output%s' % XYZList[i],
                                         lidLowOutBcl + '.color2%s' % RGBList[i])

                        cmds.connectAttr(lidLowOutBcl + '.output%s' % RGBList[i], self.judge_LR+self.name+'%sLowRoot_jnt.rotateX' % conIn)
                        cmds.connectAttr(lidUpToLowTYMinMdi + '.output%s' % XYZList[i],
                                         lidUpToLowRvs + '.input%s' % XYZList[i])
                        cmds.connectAttr(lidUpToLowRvs + '.output%s' % XYZList[i],
                                         lidUpToLowTYPlusMdi + '.input1%s' % XYZList[i])
                        cmds.setAttr(lidUpToLowTYPlusMdi + '.input2%s' % XYZList[i],
                                     -(cmds.getAttr(self.judge_LR+self.name+'%sUpRoot_jnt.jointOrientX' % conIn) + cmds.getAttr(
                                         self.judge_LR+self.name+'%sLowRoot_jnt.jointOrientX' % conIn)))
                        cmds.connectAttr(lidUpToLowRvs + '.output%s' % XYZList[i], outCds + '.firstTerm')
                        cmds.connectAttr(lidUpToLowTYPlusMdi + '.output%s' % XYZList[i], outCds + '.colorIfFalseR')
                        cmds.connectAttr(lidLowTX + '.outputX',
                                         lidLowTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowTXPma + '.output3D%s' % XYZList[i].lower(),
                                         self.judge_LR+self.name+'%sLowRoot_jnt.rotateY' % conIn)

                        if i == 1:
                            continue
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.rotateZ', lidLowRZ45Mdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidLowRZ45Mdi + '.output%s' % XYZList[i],
                                         lidLowTYPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowRZ45Mdi + '.output%s' % XYZList[i],
                                         lidLowTYRTPma + '.input3D[1].input3D%s' % XYZList[i].lower())

                elif self.judge_LR == 'r_':

                    tzOffset = -(ctlsSize / 2)

                    lidUpRoot_ctl = cmds.circle(c=(0, 0, tzOffset), nr=(0, 0, 1), sw=360, r=ctlsSize,
                                                d=3, ut=0, tol=0.01, s=8, ch=False,
                                                n=self.judge_LR + self.name + 'UpRoot_ctl')
                    lidUpRootCtlGrp = cmds.group(lidUpRoot_ctl, n=self.judge_LR + self.name + 'UpRootCtl_grp')
                    for Cvs in range(0, 3):
                        cmds.xform(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, ws=True, t=(
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[0], 4),
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[3]', w=True)[1], 4),
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[2], 4)
                        ))
                    cmds.xform(lidUpRootCtlGrp, ws=True,
                               t=cmds.xform(self.upLidCrvPointList[3], q=True, ws=True, t=True))
                    cmds.transformLimits(lidUpRoot_ctl[0], ty=(-1, 1), ety=(0, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], ty=(-1, 1), ety=(1, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], tz=(-1, 1), etx=(0, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], tz=(-1, 1), etx=(1, 1))
                    cmds.setAttr(lidUpRootCtlGrp + '.s', -distance, distance, distance)

                    lidUpTYMdi = cmds.createNode('multiplyDivide', n=self.judge_LR + self.name + 'UpTY_mdi')
                    lidUpTYPma = cmds.createNode('plusMinusAverage', n=self.judge_LR + self.name + 'UpTY_pma')
                    lidUpTXPma = cmds.createNode('plusMinusAverage', n=self.judge_LR + self.name + 'UpTX_pma')
                    lidUpRZ45Mdi = cmds.createNode('multiplyDivide', n=self.judge_LR + self.name + 'Up45RZ_mdi')
                    cmds.setAttr(lidUpRZ45Mdi + '.input2X', -45)
                    cmds.setAttr(lidUpRZ45Mdi + '.input2Z', 45)
                    cmds.setAttr(lidUpRZ45Mdi + '.operation', 2)
                    lidUpRZMdi = cmds.createNode('multiplyDivide', n=self.judge_LR + self.name + 'UpRZ_mdi')
                    lidUpTXMdi = cmds.createNode('multiplyDivide', n=self.judge_LR + self.name + 'UpTX_mdi')
                    cmds.setAttr(lidUpTXMdi + '.input2X', 10)
                    cmds.setAttr(lidUpTXMdi + '.input2Y', 20)

                    for i, AL in enumerate(alignList):

                        rotLoc = cmds.spaceLocator()
                        grp = cmds.group(rotLoc)
                        cmds.parentConstraint(self.judge_LR + self.name + '%sLowRoot_jnt' % AL, grp)
                        cmds.parentConstraint(self.judge_LR + self.name + '%sUpRoot_jnt' % AL, rotLoc[0])


                        cmds.setAttr(lidUpTYMdi + '.input2%s' % XYZList[i], cmds.getAttr(rotLoc[0]+'.rx'))

                        cmds.connectAttr(lidUpRoot_ctl[0] + '.translateY', lidUpTYMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpTYMdi + '.output%s' % XYZList[i],
                                         lidUpTYPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTYPma + '.output3D%s' % XYZList[i].lower(),
                                         self.judge_LR + self.name + '%sUpRoot_jnt.rotateX' % AL)

                        if i == 1:
                            cmds.connectAttr(lidUpTXMdi + '.outputY',
                                             lidUpTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                            cmds.connectAttr(lidUpTXPma + '.output3D%s' % XYZList[i].lower(),
                                             self.judge_LR + self.name + '%sUpRoot_jnt.rotateY' % AL)
                            cmds.delete(grp)
                            continue
                        cmds.setAttr(lidUpRZMdi + '.input2%s' % XYZList[i], cmds.getAttr(rotLoc[0]+'.rx'))
                        cmds.connectAttr(lidUpRoot_ctl[0] + '.rotateZ', lidUpRZ45Mdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpRZ45Mdi + '.output%s' % XYZList[i], lidUpRZMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpRZMdi + '.output%s' % XYZList[i],
                                         lidUpTYPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTXMdi + '.outputX',
                                         lidUpTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTXPma + '.output3D%s' % XYZList[i].lower(),
                                         self.judge_LR + self.name + '%sUpRoot_jnt.rotateY' % AL)
                        cmds.delete(grp)

                    cmds.connectAttr(lidUpRoot_ctl[0] + '.translateX', lidUpTXMdi + '.input1X')
                    cmds.connectAttr(lidUpRoot_ctl[0] + '.translateX', lidUpTXMdi + '.input1Y')

                    lidLowRoot_ctl = cmds.circle(c=(0, 0, tzOffset), nr=(0, 0, 1), sw=360, r=ctlsSize,
                                                 d=3, ut=0, tol=0.01, s=8, ch=False,
                                                 n=self.judge_LR + self.name + 'LowRoot_ctl')
                    lidLowRootCtlGrp = cmds.group(lidLowRoot_ctl, n=self.judge_LR + self.name + 'LowRootCtl_grp')
                    for Cvs in range(0, 3):
                        cmds.xform(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, ws=True, t=(
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[0], 4),
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[3]', w=True)[1], 4),
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[2], 4)
                        ))
                    cmds.xform(lidLowRootCtlGrp, ws=True,
                               t=cmds.xform(self.judge_LR + self.name + 'MidLowSpace_jnt', q=True, ws=True, t=True))
                    cmds.transformLimits(lidLowRoot_ctl[0], ty=(-1, 1), ety=(0, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], ty=(-1, 1), ety=(1, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], tz=(-1, 1), etx=(0, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], tz=(-1, 1), etx=(1, 1))
                    cmds.setAttr(lidLowRootCtlGrp + '.s', -distance, -distance, distance)

                    lidLowTYPma = cmds.createNode('plusMinusAverage', n=self.judge_LR + self.name + 'LowTY_pma')
                    lidLowTYRTPma = cmds.createNode('plusMinusAverage', n=self.judge_LR + self.name + 'LowTYRT_pma')
                    lidLowRZ45Mdi = cmds.createNode('multiplyDivide', n=self.judge_LR + self.name + 'Low45RZ_mdi')
                    cmds.setAttr(lidLowRZ45Mdi + '.input2X', -45)
                    cmds.setAttr(lidLowRZ45Mdi + '.input2Z', 45)
                    cmds.setAttr(lidLowRZ45Mdi + '.operation', 2)
                    lidLowTYMdi = cmds.createNode('multiplyDivide', n=self.judge_LR + self.name + 'LowTY_mdi')
                    lidLowTYMinMdi = cmds.createNode('multiplyDivide', n=self.judge_LR + self.name + 'LowTYMin_mdi')
                    cmds.setAttr(lidLowTYMinMdi + '.input2', -1, -1, -1)
                    lidLowOutBcl = cmds.createNode('blendColors', n=self.judge_LR + self.name + 'LowOut_bcl')
                    cmds.setAttr(lidLowOutBcl + '.blender', 1)

                    upToLowPma = cmds.createNode('plusMinusAverage', n=self.judge_LR + self.name + 'UpToLow_pma')
                    cmds.connectAttr(self.judge_LR + self.name + 'UpRoot_ctl.translateY',
                                     upToLowPma + '.input2D[0].input2Dx')
                    cmds.connectAttr(self.judge_LR + self.name + 'UpRoot_ctl.translateY',
                                     upToLowPma + '.input2D[0].input2Dy')
                    cmds.connectAttr(lidUpRZ45Mdi + '.outputX', upToLowPma + '.input2D[1].input2Dx')
                    cmds.connectAttr(lidUpRZ45Mdi + '.outputZ', upToLowPma + '.input2D[1].input2Dy')
                    lidUpToLowTYMinMdi = cmds.createNode('multiplyDivide',
                                                         n=self.judge_LR + self.name + 'UpToLowTYMin_mdi')
                    cmds.setAttr(lidUpToLowTYMinMdi + '.input2', -1, -1, -1)
                    cmds.connectAttr(upToLowPma + '.output2Dx', lidUpToLowTYMinMdi + '.input1X')
                    cmds.connectAttr(self.judge_LR + self.name + 'UpRoot_ctl.translateY',
                                     lidUpToLowTYMinMdi + '.input1Y')
                    cmds.connectAttr(upToLowPma + '.output2Dy', lidUpToLowTYMinMdi + '.input1Z')
                    lidUpToLowRvs = cmds.createNode('reverse', n=self.judge_LR + self.name + 'UpToLow_rvs')
                    lidUpToLowTYPlusMdi = cmds.createNode('multiplyDivide',
                                                          n=self.judge_LR + self.name + 'UpToLowTYPlus_mdi')
                    lidLowTX = cmds.createNode('multiplyDivide', n=self.judge_LR + self.name + 'LowTX_mdi')
                    cmds.setAttr(lidLowTX + '.input2X', -10)
                    cmds.setAttr(lidLowTX + '.input2Y', -20)
                    cmds.connectAttr(lidLowRoot_ctl[0] + '.translateX', lidLowTX + '.input1X')
                    cmds.connectAttr(lidLowRoot_ctl[0] + '.translateX', lidLowTX + '.input1Y')
                    lidLowTXPma = cmds.createNode('plusMinusAverage', n=self.judge_LR + self.name + 'LowTX_pma')

                    for i, conIn in enumerate(alignList):
                        rotLoc = cmds.spaceLocator()
                        grp = cmds.group(rotLoc)
                        cmds.parentConstraint(self.judge_LR + self.name + '%sLowRoot_jnt' % conIn, grp)
                        cmds.parentConstraint(self.judge_LR + self.name + '%sUpRoot_jnt' % conIn, rotLoc[0])

                        cmds.connectAttr(lidLowRoot_ctl[0] + '.translateY',
                                         lidLowTYPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.translateY',
                                         lidLowTYRTPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowTYPma + '.output3D%s' % XYZList[i].lower(),
                                         lidLowTYMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidLowTYRTPma + '.output3D%s' % XYZList[i].lower(),
                                         lidLowTYMinMdi + '.input1%s' % XYZList[i])
                        cmds.setAttr(lidLowTYMdi + '.input2%s' % XYZList[i], cmds.getAttr(rotLoc[0]+'.rx'))

                        outCds = cmds.createNode('condition', n=self.judge_LR + self.name + '%sLow_cds' % conIn)
                        cmds.setAttr(outCds + '.operation', 3)
                        cmds.connectAttr(lidLowTYMdi + '.output%s' % XYZList[i], outCds + '.colorIfTrueR')
                        cmds.connectAttr(lidLowTYMinMdi + '.output%s' % XYZList[i], outCds + '.secondTerm')
                        cmds.connectAttr(outCds + '.outColorR', lidLowOutBcl + '.color1%s' % RGBList[i])
                        cmds.connectAttr(lidLowTYMdi + '.output%s' % XYZList[i],
                                         lidLowOutBcl + '.color2%s' % RGBList[i])

                        cmds.connectAttr(lidLowOutBcl + '.output%s' % RGBList[i],
                                         self.judge_LR + self.name + '%sLowRoot_jnt.rotateX' % conIn)
                        cmds.connectAttr(lidUpToLowTYMinMdi + '.output%s' % XYZList[i],
                                         lidUpToLowRvs + '.input%s' % XYZList[i])
                        cmds.connectAttr(lidUpToLowRvs + '.output%s' % XYZList[i],
                                         lidUpToLowTYPlusMdi + '.input1%s' % XYZList[i])
                        cmds.setAttr(lidUpToLowTYPlusMdi + '.input2%s' % XYZList[i], -cmds.getAttr(rotLoc[0]+'.rx'))
                        cmds.connectAttr(lidUpToLowRvs + '.output%s' % XYZList[i], outCds + '.firstTerm')
                        cmds.connectAttr(lidUpToLowTYPlusMdi + '.output%s' % XYZList[i], outCds + '.colorIfFalseR')
                        cmds.connectAttr(lidLowTX + '.outputX',
                                         lidLowTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowTXPma + '.output3D%s' % XYZList[i].lower(),
                                         self.judge_LR + self.name + '%sLowRoot_jnt.rotateY' % conIn)

                        if i == 1:
                            cmds.delete(grp)
                            continue
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.rotateZ', lidLowRZ45Mdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidLowRZ45Mdi + '.output%s' % XYZList[i],
                                         lidLowTYPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowRZ45Mdi + '.output%s' % XYZList[i],
                                         lidLowTYRTPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.delete(grp)

                if not 'facialGlobalJnt_grp' in cmds.ls():
                    cmds.select(cl=True)
                    self.facialGlobalJnt = cmds.joint(n='facialGlobal_jnt')
                    facialGlobalJntGrp = cmds.group(self.facialGlobalJnt, n='facialGlobalJnt_grp')
                    cmds.xform(facialGlobalJntGrp, ws=True, t=(0, cmds.xform(self.judge_LR + 'eyeBall_jnt',
                                                                             q=True, ws=True, t=True)[1],
                                                               cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True,
                                                                          ws=True, t=True)[2]))

                self.allSkinVtxList = self.lidUpSortVtxIdList + self.lidLowSortVtxIdList
                self.allSkinJntsList = lidUpSkinEndJntsList + lidLowSkinEndJntsList

                self.allSkinWeightList = []
                self.SetNum = 1.0 / len(self.allSkinVtxList[0])
                if not self.name + 'FacialGlobal_sct' in cmds.ls():
                    self.facialGlobalSkin = cmds.skinCluster(self.polyObject, self.facialGlobalJnt,
                                                             self.allSkinJntsList,
                                                             toSelectedBones=True, n=self.name + 'FacialGlobal_sct')
                    cmds.setAttr(self.facialGlobalSkin[0] + '.skinningMethod', 1)
                    cmds.skinPercent(self.facialGlobalSkin[0], self.polyObject, tv=(self.facialGlobalJnt, 1))
                    for i, rootVtxID in enumerate(self.allSkinVtxList):
                        skinWeightList = []
                        for vi, listVtxID in enumerate(rootVtxID):
                            cmds.skinPercent(self.facialGlobalSkin[0], self.polyObject + '.vtx[%s]' % listVtxID,
                                             tv=(self.facialGlobalJnt, 1))
                            getValue = cmds.gradientControlNoAttr(self.gredient, q=True, cvv=True,
                                                                  vap=(self.SetNum * float(vi)))
                            skinWeightList.append(getValue)
                        self.allSkinWeightList.append(skinWeightList)
                    cmds.select(cl=True)
                    for i, weightIn in enumerate(self.allSkinWeightList):
                        for ini, getWeights in enumerate(weightIn):
                            cmds.skinPercent(self.facialGlobalSkin[0],
                                             self.polyObject + '.vtx[%s]' % self.allSkinVtxList[i][ini],
                                             tv=(self.allSkinJntsList[i], getWeights))

        elif cmds.checkBoxGrp(self.mirrorChesk, q=True, v1=True) == True:
            if cmds.textFieldGrp(self.names, q=True, tx=True) == '':
                mel.eval("print please_Enter_a_name")
            elif cmds.textFieldGrp(self.names, q=True, tx=True):
                self.name = cmds.textFieldGrp(self.names, q=True, tx=True)
                self.innerUpCrv = self.judge_LR + self.name + 'InnerLidUp_crv'
                self.innerLowCrv = self.judge_LR + self.name + 'InnerLidLow_crv'
                if not self.judge_LR + self.name + 'MainLidUp_crv' in cmds.ls():
                    mel.eval("print No_curve_found")
                else:
                    self.lidOtherGrp = cmds.group(em=True, n=self.judge_LR + '%s_Other_grp' % self.name)
                    cmds.setAttr(self.lidOtherGrp + '.v', False)
                    if self.lidOtherGrp[0] == 'l':
                        self.set_LR = 'r'
                    if self.lidOtherGrp[0] == 'r':
                        self.set_LR = 'l'

                    if self.judge_LR == 'r_':
                        UpVec = (0, 1, 0)
                        aimVec = (0, 0, -1)
                        OrgUpVec = (0, -1, 0)
                        OrgLowVec = (0, 1, 0)

                    if self.judge_LR == 'l_':
                        UpVec = (0, -1, 0)
                        aimVec = (0, 0, 1)
                        OrgUpVec = (0, 1, 0)
                        OrgLowVec = (0, -1, 0)

                    self.dupOtherGrp = cmds.duplicate(self.lidOtherGrp, n=self.set_LR + '_%s_Other_grp' % self.name)
                    cmds.setAttr(self.dupOtherGrp[0] + '.sx', -1)
                    self.lidUpPathCv = cmds.rebuildCurve(self.judge_LR + self.name + 'MainLidUp_crv', ch=False, rpo=0,
                                                         rt=0, end=1,
                                                         kr=0, kcp=0, kep=1,
                                                         kt=0, s=4, d=3, tol=0.01,
                                                         n=self.judge_LR + self.name + 'UpPath_crv')

                    cmds.addAttr('|' + self.lidUpPathCv[0], ln='blink', at='double', min=0, max=1, dv=0)
                    cmds.setAttr('|' + self.lidUpPathCv[0] + '.blink', e=True, keyable=True)

                    cmds.addAttr('|' + self.lidUpPathCv[0], ln='blinkSize', at='double', min=0, max=1, dv=0.3)
                    cmds.setAttr('|' + self.lidUpPathCv[0] + '.blinkSize', e=True, keyable=True)

                    self.duplicateUpPath = cmds.duplicate(self.lidUpPathCv,
                                                          n=self.set_LR + '_' + self.name + 'UpPath_crv')

                    cmds.setAttr(self.duplicateUpPath[0] + '.sx', -1)

                    lidLowPathCv = cmds.rebuildCurve(self.judge_LR + self.name + 'MainLidLow_crv', ch=False, rpo=0,
                                                     rt=0, end=1,
                                                     kr=0, kcp=0, kep=1,
                                                     kt=0, s=4, d=3, tol=0.01,
                                                     n=self.judge_LR + self.name + 'LowPath_crv')

                    self.upLidCrvPointList = [self.judge_LR + self.name + 'InCornerSpace_jnt', '',
                                         self.judge_LR + self.name + 'InUpSpace_jnt',
                                         self.judge_LR + self.name + 'MidUpSpace_jnt',
                                         self.judge_LR + self.name + 'OutUpSpace_jnt', '',
                                         self.judge_LR + self.name + 'OutCornerSpace_jnt']
                    self.LowLidCrvPointList = ['', '', self.judge_LR + self.name + 'InLowSpace_jnt',
                                          self.judge_LR + self.name + 'MidLowSpace_jnt',
                                          self.judge_LR + self.name + 'OutLowSpace_jnt', '',
                                          '']

                    self.duplicateLowPath = cmds.duplicate(lidLowPathCv,
                                                           n=self.set_LR + '_' + self.name + 'LowPath_crv')

                    cmds.setAttr(self.duplicateLowPath[0] + '.sx', -1)

                    cmds.parent(self.lidUpPathCv, lidLowPathCv, self.lidOtherGrp)
                    cmds.parent(self.duplicateUpPath, self.duplicateLowPath, self.dupOtherGrp)

                    sortUpSkinCrvJnts = []
                    sortLowSkinCrvJnts = []
                    dupSortUpSkinCrvJnts = []
                    dupSortLowSkinCrvJnts = []

                    eyeLidSpaceJntsGrp = cmds.group(em=True, n=self.judge_LR + self.name + 'SpaceJntsGrp')

                    self.lidDupSpaceJntsGrp = cmds.duplicate(eyeLidSpaceJntsGrp,
                                                             n=self.set_LR + '_' + self.name + 'SpaceJntsGrp')

                    for i, s in enumerate(self.upLidCrvPointList):
                        if i == 1 or i == 5:
                            continue
                        cmds.select(cl=True)
                        lidUpSpaceJnt = cmds.joint(
                            p=cmds.pointPosition(self.judge_LR + self.name + 'UpPath_crv.cv[%s]' % i), n=s)
                        cmds.setAttr(lidUpSpaceJnt + '.drawStyle', 2)
                        lidUpEndJnt = cmds.joint(
                            p=cmds.pointPosition(self.judge_LR + self.name + 'UpPath_crv.cv[%s]' % i),
                            n=s.replace('Space', 'End'))
                        if self.judge_LR == 'l_':
                            cmds.setAttr(lidUpSpaceJnt + '.jointOrientX', 0)
                            cmds.setAttr(lidUpSpaceJnt + '.jointOrientY', 0)
                        elif self.judge_LR == 'r_':
                            cmds.setAttr(lidUpSpaceJnt + '.jointOrientX', 180)
                            cmds.setAttr(lidUpSpaceJnt + '.jointOrientY', 0)
                        sortUpSkinCrvJnts.append(lidUpEndJnt)

                    for i, s in enumerate(self.LowLidCrvPointList):
                        if i == 0 or i == 1 or i == 5 or i == 6:
                            continue
                        cmds.select(cl=True)
                        lidLowSpaceJnt = cmds.joint(
                            p=cmds.pointPosition(self.judge_LR + self.name + 'LowPath_crv.cv[%s]' % i), n=s)
                        cmds.setAttr(lidLowSpaceJnt + '.drawStyle', 2)
                        lidLowEndJnt = cmds.joint(
                            p=cmds.pointPosition(self.judge_LR + self.name + 'LowPath_crv.cv[%s]' % i),
                            n=s.replace('Space', 'End'))
                        if self.judge_LR == 'l_':
                            cmds.setAttr(lidLowSpaceJnt + '.jointOrientX', 180)
                            cmds.setAttr(lidLowSpaceJnt + '.jointOrientY', 180)
                        elif self.judge_LR == 'r_':
                            cmds.setAttr(lidLowSpaceJnt + '.jointOrientX', 0)
                            cmds.setAttr(lidLowSpaceJnt + '.jointOrientY', 180)

                        sortLowSkinCrvJnts.append(lidLowEndJnt)

                    for i, s in enumerate(self.upLidCrvPointList):
                        if i == 1 or i == 5:
                            continue
                        cmds.select(cl=True)
                        if i == 0:
                            self.lidUpIcRootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, self.lidUpIcRootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.upLidCrvPointList[-1]))
                            cmds.makeIdentity(self.lidUpIcRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.upLidCrvPointList[i], self.lidUpIcRootJnt)
                            cmds.parent(self.lidUpIcRootJnt, eyeLidSpaceJntsGrp)
                        elif i == 2:
                            lidUpIRootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, lidUpIRootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.LowLidCrvPointList[2]))
                            cmds.makeIdentity(lidUpIRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.upLidCrvPointList[i], lidUpIRootJnt)
                            cmds.parent(lidUpIRootJnt, eyeLidSpaceJntsGrp)
                        elif i == 3:
                            self.lidUpMRootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, self.lidUpMRootJnt, offset=(0, 0, 0), weight=1,
                                                   aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.LowLidCrvPointList[3]))
                            cmds.makeIdentity(self.lidUpMRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.upLidCrvPointList[i], self.lidUpMRootJnt)
                            cmds.parent(self.lidUpMRootJnt, eyeLidSpaceJntsGrp)
                        elif i == 4:
                            self.lidUpORootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, self.lidUpORootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.LowLidCrvPointList[4]))
                            cmds.makeIdentity(self.lidUpORootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.upLidCrvPointList[i], self.lidUpORootJnt)
                            cmds.parent(self.lidUpORootJnt, eyeLidSpaceJntsGrp)
                        elif i == 6:
                            self.lidUpOCRootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, self.lidUpOCRootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.upLidCrvPointList[0]))
                            cmds.makeIdentity(self.lidUpOCRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.upLidCrvPointList[i], self.lidUpOCRootJnt)
                            cmds.parent(self.lidUpOCRootJnt, eyeLidSpaceJntsGrp)

                    for selJnt in sortUpSkinCrvJnts:
                        mirrodSpaceJnts = cmds.mirrorJoint(
                            cmds.listRelatives(cmds.listRelatives(selJnt, p=True), p=True), mirrorYZ=True,
                            mirrorBehavior=True,
                            searchReplace=(self.judge_LR + self.name,
                                           self.set_LR + '_' + self.name))

                        cmds.parent(mirrodSpaceJnts[0], self.lidDupSpaceJntsGrp)
                        dupSortUpSkinCrvJnts.append(mirrodSpaceJnts[-1])

                    for i, s in enumerate(self.LowLidCrvPointList):
                        if i == 0 or i == 1 or i == 5 or i == 6:
                            continue
                        cmds.select(cl=True)
                        if i == 2:
                            lidLowIRootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, lidLowIRootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.upLidCrvPointList[2]))
                            cmds.makeIdentity(lidLowIRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.LowLidCrvPointList[i], lidLowIRootJnt)
                            cmds.parent(lidLowIRootJnt, eyeLidSpaceJntsGrp)
                        elif i == 3:
                            self.lidLowMRootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, self.lidLowMRootJnt, offset=(0, 0, 0), weight=1,
                                                   aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.upLidCrvPointList[3]))
                            cmds.makeIdentity(self.lidLowMRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.LowLidCrvPointList[i], self.lidLowMRootJnt)
                            cmds.parent(self.lidLowMRootJnt, eyeLidSpaceJntsGrp)
                        elif i == 4:
                            self.lidLowORootJnt = cmds.joint(
                                p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True),
                                n=s.replace('Space', 'Root'))
                            cmds.delete(
                                cmds.aimConstraint(s, self.lidLowORootJnt, offset=(0, 0, 0), weight=1, aimVector=aimVec,
                                                   upVector=UpVec,
                                                   worldUpType=('object'), worldUpObject=self.upLidCrvPointList[4]))
                            cmds.makeIdentity(self.lidLowORootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                            cmds.parent(self.LowLidCrvPointList[i], self.lidLowORootJnt)
                            cmds.parent(self.lidLowORootJnt, eyeLidSpaceJntsGrp)

                    for selJnt in sortLowSkinCrvJnts:
                        mirrodSpaceJnts = cmds.mirrorJoint(
                            cmds.listRelatives(cmds.listRelatives(selJnt, p=True), p=True), mirrorYZ=True,
                            mirrorBehavior=True,
                            searchReplace=(self.judge_LR + self.name,
                                           self.set_LR + '_' + self.name))

                        cmds.parent(mirrodSpaceJnts[0], self.lidDupSpaceJntsGrp)
                        dupSortLowSkinCrvJnts.append(mirrodSpaceJnts[-1])

                cmds.skinCluster(sortUpSkinCrvJnts, self.judge_LR + self.name + 'UpPath_crv', tsb=True,
                                 n=self.judge_LR + self.name + 'UpCrv_sct')
                cmds.skinPercent(self.judge_LR + self.name + 'UpCrv_sct',
                                 self.judge_LR + self.name + 'UpPath_crv.cv[1]',
                                 transformValue=[(sortUpSkinCrvJnts[0], 0.6), (sortUpSkinCrvJnts[1], 0.4)])
                cmds.skinPercent(self.judge_LR + self.name + 'UpCrv_sct',
                                 self.judge_LR + self.name + 'UpPath_crv.cv[5]',
                                 transformValue=[(sortUpSkinCrvJnts[3], 0.4), (sortUpSkinCrvJnts[4], 0.6)])

                cmds.skinCluster(sortUpSkinCrvJnts[0], sortLowSkinCrvJnts, sortUpSkinCrvJnts[4],
                                 self.judge_LR + self.name + 'LowPath_crv', tsb=True,
                                 n=self.judge_LR + self.name + 'LowCrv_sct')
                cmds.skinPercent(self.judge_LR + self.name + 'LowCrv_sct',
                                 self.judge_LR + self.name + 'LowPath_crv.cv[1]',
                                 transformValue=[(sortUpSkinCrvJnts[0], 0.6), (sortLowSkinCrvJnts[0], 0.4)])
                cmds.skinPercent(self.judge_LR + self.name + 'LowCrv_sct',
                                 self.judge_LR + self.name + 'LowPath_crv.cv[5]',
                                 transformValue=[(sortUpSkinCrvJnts[4], 0.6), (sortLowSkinCrvJnts[2], 0.4)])

                cmds.skinCluster(dupSortUpSkinCrvJnts, self.set_LR + '_' + self.name + 'UpPath_crv', tsb=True,
                                 n=self.set_LR + '_' + self.name + 'UpCrv_sct')
                cmds.skinPercent(self.set_LR + '_' + self.name + 'UpCrv_sct',
                                 self.set_LR + '_' + self.name + 'UpPath_crv.cv[1]',
                                 transformValue=[(dupSortUpSkinCrvJnts[0], 0.6), (dupSortUpSkinCrvJnts[1], 0.4)])
                cmds.skinPercent(self.set_LR + '_' + self.name + 'UpCrv_sct',
                                 self.set_LR + '_' + self.name + 'UpPath_crv.cv[5]',
                                 transformValue=[(dupSortUpSkinCrvJnts[3], 0.4), (dupSortUpSkinCrvJnts[4], 0.6)])

                cmds.skinCluster(dupSortUpSkinCrvJnts[0], dupSortLowSkinCrvJnts, dupSortUpSkinCrvJnts[4],
                                 self.set_LR + '_' + self.name + 'LowPath_crv', tsb=True,
                                 n=self.set_LR + '_' + self.name + 'LowCrv_sct')
                cmds.skinPercent(self.set_LR + '_' + self.name + 'LowCrv_sct',
                                 self.set_LR + '_' + self.name + 'LowPath_crv.cv[1]',
                                 transformValue=[(dupSortUpSkinCrvJnts[0], 0.6), (dupSortLowSkinCrvJnts[0], 0.4)])
                cmds.skinPercent(self.set_LR + '_' + self.name + 'LowCrv_sct',
                                 self.set_LR + '_' + self.name + 'LowPath_crv.cv[5]',
                                 transformValue=[(dupSortUpSkinCrvJnts[4], 0.6), (dupSortLowSkinCrvJnts[2], 0.4)])

                MlidUpCrvList = api.MSelectionList()
                MlidUpCrvList.add(self.judge_LR + self.name + 'MainLidUp_crv')
                MlidUpCrvList.add(self.judge_LR + self.name + 'UpPath_crv')
                MlidUpCrvDag = MlidUpCrvList.getDagPath(0)
                MlidUpPathDag = MlidUpCrvList.getDagPath(1)
                MFn_lipUpCrv = api.MFnNurbsCurve(MlidUpCrvDag)
                MFn_lipUpPathCrv = api.MFnNurbsCurve(MlidUpPathDag)
                lidUpCvPosList = [index for index in MFn_lipUpCrv.cvPositions()]
                lidUpAimLocsGrp = cmds.group(em=True, n=self.judge_LR + self.name + 'UpAimLocs_grp')
                cmds.setAttr(lidUpAimLocsGrp + '.v', False)
                cmds.parent(lidUpAimLocsGrp, self.lidOtherGrp)
                dupLidUpAimLocsGrp = cmds.group(em=True, n=self.set_LR + '_' + self.name + 'UpAimLocs_grp')
                cmds.setAttr(dupLidUpAimLocsGrp + '.v', False)
                cmds.parent(dupLidUpAimLocsGrp, self.dupOtherGrp)
                getArclen = (cmds.arclen(self.judge_LR + self.name + 'UpPath_crv') * 0.001)
                lidUpTargetLocList = []
                dupLidUpTargetLocList = []
                for i, Mpoints in enumerate(lidUpCvPosList):
                    getLidUpCrvdisToPoint = MFn_lipUpPathCrv.distanceToPoint(Mpoints, api.MSpace.kObject)
                    getUpCrvParam = MFn_lipUpPathCrv.getParamAtPoint(Mpoints, getLidUpCrvdisToPoint + getArclen,
                                                                     api.MSpace.kObject)
                    aimUpLoc = cmds.spaceLocator(n=self.judge_LR + self.name + 'Aim%sUp_loc' % i)
                    lidUpTargetLocList.append(aimUpLoc[0])
                    cmds.setAttr(cmds.listRelatives(aimUpLoc[0])[0] + '.localScale', 0.01, 0.01, 0.01)
                    aimUpGrp = cmds.group(aimUpLoc, n=self.judge_LR + self.name + 'Aim%sUpLoc_grp' % i)
                    lidUpPci = cmds.createNode('pointOnCurveInfo', n=self.judge_LR + self.name + 'Aim%s_pci' % i)

                    cmds.connectAttr(cmds.listRelatives(self.judge_LR + self.name + 'UpPath_crv')[0] + '.worldSpace[0]',
                                     lidUpPci + '.inputCurve')
                    cmds.setAttr(lidUpPci + '.parameter', getUpCrvParam)
                    cmds.connectAttr(lidUpPci + '.positionX', aimUpGrp + '.translateX')
                    cmds.connectAttr(lidUpPci + '.positionY', aimUpGrp + '.translateY')
                    cmds.connectAttr(lidUpPci + '.positionZ', aimUpGrp + '.translateZ')
                    cmds.parent(aimUpGrp, lidUpAimLocsGrp)

                    dupAimUpLoc = cmds.spaceLocator(n=self.set_LR + '_' + self.name + 'Aim%sUp_loc' % i)
                    dupLidUpTargetLocList.append(dupAimUpLoc[0])
                    cmds.setAttr(cmds.listRelatives(dupAimUpLoc[0])[0] + '.localScale', 0.01, 0.01, 0.01)
                    dupAimUpGrp = cmds.group(dupAimUpLoc, n=self.set_LR + '_' + self.name + 'Aim%sUpLoc_grp' % i)
                    dupLidUpPci = cmds.createNode('pointOnCurveInfo', n=self.set_LR + '_' + self.name + 'Aim%s_pci' % i)

                    cmds.connectAttr(
                        cmds.listRelatives(self.set_LR + '_' + self.name + 'UpPath_crv')[0] + '.worldSpace[0]',
                        dupLidUpPci + '.inputCurve')
                    cmds.setAttr(dupLidUpPci + '.parameter', getUpCrvParam)
                    cmds.connectAttr(dupLidUpPci + '.positionX', dupAimUpGrp + '.translateX')
                    cmds.connectAttr(dupLidUpPci + '.positionY', dupAimUpGrp + '.translateY')
                    cmds.connectAttr(dupLidUpPci + '.positionZ', dupAimUpGrp + '.translateZ')
                    cmds.parent(dupAimUpGrp, dupLidUpAimLocsGrp)

                MlidLowCrvList = api.MSelectionList()
                MlidLowCrvList.add(self.judge_LR + self.name + 'MainLidLow_crv')
                MlidLowCrvList.add(self.judge_LR + self.name + 'LowPath_crv')
                MlidLowCrvDag = MlidLowCrvList.getDagPath(0)
                MlidLowPathDag = MlidLowCrvList.getDagPath(1)
                MFn_lipLowCrv = api.MFnNurbsCurve(MlidLowCrvDag)
                MFn_lipLowPathCrv = api.MFnNurbsCurve(MlidLowPathDag)
                lidLowCvPosList = [index for index in MFn_lipLowCrv.cvPositions()]
                lidLowAimLocsGrp = cmds.group(em=True, n=self.judge_LR + self.name + 'LowAimLocs_grp')
                cmds.setAttr(lidLowAimLocsGrp + '.v', False)
                cmds.parent(lidLowAimLocsGrp, self.lidOtherGrp)
                dupLidLowAimLocsGrp = cmds.group(em=True, n=self.set_LR + '_' + self.name + 'LowAimLocs_grp')
                cmds.setAttr(dupLidLowAimLocsGrp + '.v', False)
                cmds.parent(dupLidLowAimLocsGrp, self.dupOtherGrp)

                lidLowTargetLocList = []
                dupLidLowTargetLocList = []
                for i, Mpoints in enumerate(lidLowCvPosList):
                    if i == 0 or i == len(lidLowCvPosList) - 1:
                        continue
                    getLidLowCrvdisToPoint = MFn_lipLowPathCrv.distanceToPoint(Mpoints, api.MSpace.kObject)
                    getLowCrvParam = MFn_lipLowPathCrv.getParamAtPoint(Mpoints, getLidLowCrvdisToPoint + getArclen,
                                                                       api.MSpace.kObject)
                    aimLowLoc = cmds.spaceLocator(n=self.judge_LR + self.name + 'Aim%sLow_loc' % i)
                    lidLowTargetLocList.append(aimLowLoc[0])
                    cmds.setAttr(cmds.listRelatives(aimLowLoc[0])[0] + '.localScale', 0.01, 0.01, 0.01)
                    aimLowGrp = cmds.group(aimLowLoc, n=self.judge_LR + self.name + 'Aim%sLowLoc_grp' % i)
                    lidLowPci = cmds.createNode('pointOnCurveInfo', n=self.judge_LR + self.name + 'Aim%s_pci' % i)

                    cmds.connectAttr(
                        cmds.listRelatives(self.judge_LR + self.name + 'LowPath_crv')[0] + '.worldSpace[0]',
                        lidLowPci + '.inputCurve')
                    cmds.setAttr(lidLowPci + '.parameter', getLowCrvParam)
                    cmds.connectAttr(lidLowPci + '.positionX', aimLowGrp + '.translateX')
                    cmds.connectAttr(lidLowPci + '.positionY', aimLowGrp + '.translateY')
                    cmds.connectAttr(lidLowPci + '.positionZ', aimLowGrp + '.translateZ')
                    cmds.parent(aimLowGrp, lidLowAimLocsGrp)

                    dupAimLowLoc = cmds.spaceLocator(n=self.set_LR + '_' + self.name + 'Aim%sLow_loc' % i)
                    dupLidLowTargetLocList.append(dupAimLowLoc[0])
                    cmds.setAttr(cmds.listRelatives(dupAimLowLoc[0])[0] + '.localScale', 0.01, 0.01, 0.01)
                    dupAimLowGrp = cmds.group(dupAimLowLoc, n=self.set_LR + '_' + self.name + 'Aim%sLowLoc_grp' % i)
                    dupLidLowPci = cmds.createNode('pointOnCurveInfo',
                                                   n=self.set_LR + '_' + self.name + 'Aim%s_pci' % i)

                    cmds.connectAttr(
                        cmds.listRelatives(self.set_LR + '_' + self.name + 'LowPath_crv')[0] + '.worldSpace[0]',
                        dupLidLowPci + '.inputCurve')
                    cmds.setAttr(dupLidLowPci + '.parameter', getLowCrvParam)
                    cmds.connectAttr(dupLidLowPci + '.positionX', dupAimLowGrp + '.translateX')
                    cmds.connectAttr(dupLidLowPci + '.positionY', dupAimLowGrp + '.translateY')
                    cmds.connectAttr(dupLidLowPci + '.positionZ', dupAimLowGrp + '.translateZ')
                    cmds.parent(dupAimLowGrp, dupLidLowAimLocsGrp)

                cmds.delete(self.OtherCrvGrp)
                cmds.select(cl=True)

                lidOrgGrp = cmds.group(em=True, n=self.judge_LR + '%sOrgJnts_grp' % self.name)
                cmds.setAttr(lidOrgGrp + '.v', False)
                lidSkinJntsGrp = cmds.group(em=True, n=self.judge_LR + '%sSkinJnts_grp' % self.name)
                cmds.setAttr(lidSkinJntsGrp + '.v', False)

                dupLidOrgGrp = cmds.group(em=True, n=self.set_LR + '_' + '%sOrgJnts_grp' % self.name)
                cmds.setAttr(dupLidOrgGrp + '.v', False)
                dupLidSkinJntsGrp = cmds.group(em=True, n=self.set_LR + '_' + '%sSkinJnts_grp' % self.name)
                cmds.setAttr(dupLidSkinJntsGrp + '.v', False)

                lidUpOrgList = []
                lidLowOrgList = []

                lidUpSkinJntsList = []
                lidLowSkinJntsList = []

                lidUpSkinEndJntsList = []
                lidLowSkinEndJntsList = []

                duplidUpOrgList = []
                duplidLowOrgList = []

                duplidUpSkinJntsList = []
                duplidLowSkinJntsList = []

                duplidUpSkinEndJntsList = []
                duplidLowSkinEndJntsList = []

                for i, aimLocIndex in enumerate(lidUpTargetLocList):
                    if i == 0 or i == len(lidUpTargetLocList) - 1:
                        continue
                    cmds.select(cl=True)
                    lidUpOrgJnt = cmds.joint(n=aimLocIndex.replace('_loc', 'Org_jnt'),
                                             p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True))
                    lidUpOrgList.append(lidUpOrgJnt)
                    cmds.select(cl=True)
                    lidUpOrgEndJnt = cmds.joint(n=aimLocIndex.replace('_loc', 'OrgEnd_jnt'),
                                                p=cmds.xform(aimLocIndex, q=True, ws=True, t=True))
                    cmds.select(cl=True)
                    lidUpSkinRootJnt = cmds.joint(
                        n=self.judge_LR + '%sUpLidSkinRoot%s_jnt' % (self.name, str(i).zfill(2)),
                        p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True))
                    cmds.setAttr(lidUpSkinRootJnt + '.drawStyle', 2)

                    cmds.select(cl=True)
                    lidUpSkinEndJnt = cmds.joint(
                        n=self.judge_LR + '%sUpLidSkinEnd%s_jnt' % (self.name, str(i).zfill(2)),
                        p=cmds.xform(aimLocIndex, q=True, ws=True, t=True))
                    lidUpSkinEndJntsList.append(lidUpSkinEndJnt)
                    cmds.setAttr(lidUpSkinEndJnt + '.radius', 0.1)

                    lidUpSkinJntsList.append(lidUpSkinRootJnt)
                    cmds.delete(
                        cmds.aimConstraint(aimLocIndex, lidUpOrgJnt, offset=(0, 0, 0), weight=1, aimVector=(0, 0, 1),
                                           upVector=OrgLowVec,
                                           worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                           worldUpObject=(self.lidUpMRootJnt)))
                    cmds.makeIdentity(lidUpOrgJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                    cmds.parent(lidUpOrgEndJnt, lidUpOrgJnt)
                    cmds.aimConstraint(aimLocIndex, lidUpOrgJnt, offset=(0, 0, 0), weight=1, aimVector=(0, 0, 1),
                                       upVector=OrgLowVec,
                                       worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                       worldUpObject=(self.lidUpMRootJnt), n=lidUpOrgJnt.replace('_jnt', '_aim'))
                    cmds.parent(lidUpOrgJnt, lidOrgGrp)

                    cmds.setAttr(lidUpSkinEndJnt + '.jointOrient', 0, 0, 0)
                    cmds.setAttr(lidUpSkinRootJnt + '.jointOrient', cmds.getAttr(lidUpOrgJnt + '.jointOrientX'),
                                 cmds.getAttr(lidUpOrgJnt + '.jointOrientY'),
                                 cmds.getAttr(lidUpOrgJnt + '.jointOrientZ'))
                    cmds.parent(lidUpSkinEndJnt, lidUpSkinRootJnt)
                    cmds.parent(lidUpSkinRootJnt, lidSkinJntsGrp)

                for i, aimLocIndex in enumerate(dupLidUpTargetLocList):
                    if i == 0 or i == len(dupLidUpTargetLocList) - 1:
                        continue
                    cmds.select(cl=True)
                    duplidUpOrgJnt = cmds.joint(n=aimLocIndex.replace('_loc', 'Org_jnt'),
                                                p=cmds.xform(self.set_LR + '_' + 'eyeBall_jnt', q=True, ws=True,
                                                             t=True))
                    duplidUpOrgList.append(duplidUpOrgJnt)
                    cmds.select(cl=True)
                    duplidUpOrgEndJnt = cmds.joint(n=aimLocIndex.replace('_loc', 'OrgEnd_jnt'),
                                                   p=cmds.xform(aimLocIndex, q=True, ws=True, t=True))
                    cmds.select(cl=True)
                    duplidUpSkinRootJnt = cmds.joint(
                        n=self.set_LR + '_' + '%sUpLidSkinRoot%s_jnt' % (self.name, str(i).zfill(2)),
                        p=cmds.xform(self.set_LR + '_' + 'eyeBall_jnt', q=True, ws=True, t=True))
                    cmds.setAttr(duplidUpSkinRootJnt + '.drawStyle', 2)

                    cmds.select(cl=True)
                    duplidUpSkinEndJnt = cmds.joint(
                        n=self.set_LR + '_' + '%sUpLidSkinEnd%s_jnt' % (self.name, str(i).zfill(2)),
                        p=cmds.xform(aimLocIndex, q=True, ws=True, t=True))
                    duplidUpSkinEndJntsList.append(duplidUpSkinEndJnt)
                    cmds.setAttr(duplidUpSkinEndJnt + '.radius', 0.1)

                    duplidUpSkinJntsList.append(duplidUpSkinRootJnt)
                    cmds.delete(
                        cmds.aimConstraint(aimLocIndex, duplidUpOrgJnt, offset=(0, 0, 0), weight=1, aimVector=(0, 0, 1),
                                           upVector=OrgLowVec,
                                           worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                           worldUpObject=(dupSortUpSkinCrvJnts[1])))
                    cmds.makeIdentity(duplidUpOrgJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                    cmds.parent(duplidUpOrgEndJnt, duplidUpOrgJnt)
                    cmds.aimConstraint(aimLocIndex, duplidUpOrgJnt, offset=(0, 0, 0), weight=1, aimVector=(0, 0, 1),
                                       upVector=OrgLowVec,
                                       worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                       worldUpObject=(dupSortUpSkinCrvJnts[1]),
                                       n=duplidUpOrgJnt.replace('_jnt', '_aim'))
                    cmds.parent(duplidUpOrgJnt, dupLidOrgGrp)

                    cmds.setAttr(duplidUpSkinEndJnt + '.jointOrient', 0, 0, 0)
                    cmds.setAttr(duplidUpSkinRootJnt + '.jointOrient', cmds.getAttr(duplidUpOrgJnt + '.jointOrientX'),
                                 cmds.getAttr(duplidUpOrgJnt + '.jointOrientY'),
                                 cmds.getAttr(duplidUpOrgJnt + '.jointOrientZ'))
                    cmds.parent(duplidUpSkinEndJnt, duplidUpSkinRootJnt)
                    cmds.parent(duplidUpSkinRootJnt, dupLidSkinJntsGrp)

                for i, aimLocIndex in enumerate(lidLowTargetLocList):
                    cmds.select(cl=True)
                    lidLowOrgJnt = cmds.joint(n=aimLocIndex.replace('_loc', 'Org_jnt'),
                                              p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True))
                    lidLowOrgList.append(lidLowOrgJnt)
                    cmds.select(cl=True)
                    lidLowOrgEndJnt = cmds.joint(n=aimLocIndex.replace('_loc', 'OrgEnd_jnt'),
                                                 p=cmds.xform(aimLocIndex, q=True, ws=True, t=True))

                    cmds.select(cl=True)
                    lidLowSkinRootJnt = cmds.joint(
                        n=self.judge_LR + '%sLowLidSkinRoot%s_jnt' % (self.name, str(i + 1).zfill(2)),
                        p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True))
                    cmds.setAttr(lidLowSkinRootJnt + '.drawStyle', 2)

                    cmds.select(cl=True)
                    lidLowSkinEndJnt = cmds.joint(
                        n=self.judge_LR + '%sLowLidSkinEnd%s_jnt' % (self.name, str(i + 1).zfill(2)),
                        p=cmds.xform(aimLocIndex, q=True, ws=True, t=True))
                    cmds.setAttr(lidLowSkinEndJnt + '.radius', 0.1)

                    lidLowSkinEndJntsList.append(lidLowSkinEndJnt)
                    lidLowSkinJntsList.append(lidLowSkinRootJnt)

                    cmds.delete(
                        cmds.aimConstraint(aimLocIndex, lidLowOrgJnt, offset=(0, 0, 0), weight=1, aimVector=(0, 0, 1),
                                           upVector=OrgUpVec,
                                           worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                           worldUpObject=(self.lidLowMRootJnt)))
                    cmds.makeIdentity(lidLowOrgJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                    cmds.parent(lidLowOrgEndJnt, lidLowOrgJnt)
                    cmds.aimConstraint(aimLocIndex, lidLowOrgJnt, offset=(0, 0, 0), weight=1, aimVector=(0, 0, 1),
                                       upVector=OrgUpVec,
                                       worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                       worldUpObject=(self.lidLowMRootJnt), n=lidLowOrgJnt.replace('_jnt', '_aim'))
                    cmds.parent(lidLowOrgJnt, lidOrgGrp)

                    cmds.setAttr(lidLowSkinEndJnt + '.jointOrient', 0, 0, 0)
                    cmds.setAttr(lidLowSkinRootJnt + '.jointOrient', cmds.getAttr(lidLowOrgJnt + '.jointOrientX'),
                                 cmds.getAttr(lidLowOrgJnt + '.jointOrientY'),
                                 cmds.getAttr(lidLowOrgJnt + '.jointOrientZ'))
                    cmds.parent(lidLowSkinEndJnt, lidLowSkinRootJnt)
                    cmds.parent(lidLowSkinRootJnt, lidSkinJntsGrp)

                for i, aimLocIndex in enumerate(dupLidLowTargetLocList):
                    cmds.select(cl=True)
                    duplidLowOrgJnt = cmds.joint(n=aimLocIndex.replace('_loc', 'Org_jnt'),
                                                 p=cmds.xform(self.set_LR + '_' + 'eyeBall_jnt', q=True, ws=True,
                                                              t=True))
                    duplidLowOrgList.append(duplidLowOrgJnt)
                    cmds.select(cl=True)
                    duplidLowOrgEndJnt = cmds.joint(n=aimLocIndex.replace('_loc', 'OrgEnd_jnt'),
                                                    p=cmds.xform(aimLocIndex, q=True, ws=True, t=True))

                    cmds.select(cl=True)
                    duplidLowSkinRootJnt = cmds.joint(
                        n=self.set_LR + '_' + '%sLowLidSkinRoot%s_jnt' % (self.name, str(i + 1).zfill(2)),
                        p=cmds.xform(self.set_LR + '_' + 'eyeBall_jnt', q=True, ws=True, t=True))
                    cmds.setAttr(duplidLowSkinRootJnt + '.drawStyle', 2)

                    cmds.select(cl=True)
                    duplidLowSkinEndJnt = cmds.joint(
                        n=self.set_LR + '_' + '%sLowLidSkinEnd%s_jnt' % (self.name, str(i + 1).zfill(2)),
                        p=cmds.xform(aimLocIndex, q=True, ws=True, t=True))
                    cmds.setAttr(duplidLowSkinEndJnt + '.radius', 0.1)

                    duplidLowSkinEndJntsList.append(duplidLowSkinEndJnt)
                    duplidLowSkinJntsList.append(duplidLowSkinRootJnt)

                    cmds.delete(
                        cmds.aimConstraint(aimLocIndex, duplidLowOrgJnt, offset=(0, 0, 0), weight=1, aimVector=(0, 0, 1),
                                           upVector=OrgUpVec,
                                           worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                           worldUpObject=(cmds.listRelatives(cmds.listRelatives(dupSortLowSkinCrvJnts[1], p=True)[0], p=True)[0])))

                    cmds.makeIdentity(duplidLowOrgJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)
                    cmds.parent(duplidLowOrgEndJnt, duplidLowOrgJnt)
                    cmds.aimConstraint(aimLocIndex, duplidLowOrgJnt, offset=(0, 0, 0), weight=1, aimVector=(0, 0, 1),
                                       upVector=OrgUpVec,
                                       worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                       worldUpObject=(cmds.listRelatives(cmds.listRelatives(dupSortLowSkinCrvJnts[1], p=True)[0], p=True)[0]),
                                       n=duplidLowOrgJnt.replace('_jnt', '_aim'))
                    cmds.parent(duplidLowOrgJnt, dupLidOrgGrp)

                    cmds.setAttr(duplidLowSkinEndJnt + '.jointOrient', 0, 0, 0)
                    cmds.setAttr(duplidLowSkinRootJnt + '.jointOrient', cmds.getAttr(duplidLowOrgJnt + '.jointOrientX'),
                                 cmds.getAttr(duplidLowOrgJnt + '.jointOrientY'),
                                 cmds.getAttr(duplidLowOrgJnt + '.jointOrientZ'))
                    cmds.parent(duplidLowSkinEndJnt, duplidLowSkinRootJnt)
                    cmds.parent(duplidLowSkinRootJnt, dupLidSkinJntsGrp)

                lidUpOctList = []
                lidLowOctList = []

                duplidUpOctList = []
                duplidLowOctList = []

                for i, lidUpSkinJnts in enumerate(lidUpSkinJntsList):
                    lidUpOct = cmds.orientConstraint(lidUpOrgList[i], lidLowOrgList[i], lidUpSkinJnts,
                                                     offset=(0, 0, 0), weight=1,
                                                     n=self.judge_LR + '%sUpConstructor%s_oct' % (
                                                         self.name, str(i + 1).zfill(2)))
                    cmds.setAttr(lidUpOct[0] + '.interpType', 2)
                    lidUpOctList.append(lidUpOct[0])

                    lidLowOct = cmds.orientConstraint(lidLowOrgList[i], lidUpOrgList[i], lidLowSkinJntsList[i],
                                                      offset=(0, 0, 0),
                                                      weight=1,
                                                      n=self.judge_LR + '%sLowConstructor%s_oct' % (
                                                          self.name, str(i + 1).zfill(2)))
                    cmds.setAttr(lidLowOct[0] + '.interpType', 2)
                    lidLowOctList.append(lidLowOct[0])
                cmds.select(cl=True)

                lidBlinkRvs = cmds.createNode('reverse', n=self.judge_LR + '%slidBlink_rvs' % self.name)
                lidUpSRmv = cmds.createNode('remapValue', n=self.judge_LR + '%sUpLidStart_rmv' % self.name)
                lidUpERmv = cmds.createNode('remapValue', n=self.judge_LR + '%sUpLidEnd_rmv' % self.name)
                lidLowSRmv = cmds.createNode('remapValue', n=self.judge_LR + '%sLowLidStart_rmv' % self.name)
                lidLowERmv = cmds.createNode('remapValue', n=self.judge_LR + '%sLowLidEnd_rmv' % self.name)

                cmds.connectAttr(self.lidUpPathCv[0] + '.blink', lidUpSRmv + '.inputValue')
                cmds.connectAttr(self.lidUpPathCv[0] + '.blinkSize', lidUpSRmv + '.outputMax')
                cmds.connectAttr(self.lidUpPathCv[0] + '.blink', lidUpERmv + '.inputValue')
                cmds.connectAttr(self.lidUpPathCv[0] + '.blinkSize', lidBlinkRvs + '.inputX')
                cmds.connectAttr(lidBlinkRvs + '.outputX', lidUpERmv + '.outputMax')

                cmds.connectAttr(self.lidUpPathCv[0] + '.blink', lidLowSRmv + '.inputValue')
                cmds.connectAttr(lidBlinkRvs + '.outputX', lidLowSRmv + '.outputMax')
                cmds.connectAttr(self.lidUpPathCv[0] + '.blink', lidLowERmv + '.inputValue')
                cmds.connectAttr(self.lidUpPathCv[0] + '.blinkSize', lidLowERmv + '.outputMax')

                cmds.setAttr(lidUpSRmv + '.outputMin', 1)
                cmds.setAttr(lidLowSRmv + '.outputMin', 1)

                for i, indexUpOct in enumerate(lidUpOctList):
                    cmds.connectAttr(lidUpSRmv + '.outValue', indexUpOct + '.' + lidUpOrgList[i] + 'W0')
                    cmds.connectAttr(lidUpERmv + '.outValue', indexUpOct + '.' + lidLowOrgList[i] + 'W1')

                for i, indexLowOct in enumerate(lidLowOctList):
                    cmds.connectAttr(lidLowSRmv + '.outValue', indexLowOct + '.' + lidLowOrgList[i] + 'W0')
                    cmds.connectAttr(lidLowERmv + '.outValue', indexLowOct + '.' + lidUpOrgList[i] + 'W1')

                cmds.select(cl=True)
                lidInCSkinRootJnt = cmds.joint(n=self.judge_LR + '%sUpLidSkinRoot0_jnt' % self.name,
                                               p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True))
                cmds.setAttr(lidInCSkinRootJnt + '.drawStyle', 2)
                cmds.setAttr(lidInCSkinRootJnt + '.jointOrient', cmds.getAttr(self.lidUpIcRootJnt + '.jointOrientX'),
                             cmds.getAttr(self.lidUpIcRootJnt + '.jointOrientY'),
                             cmds.getAttr(self.lidUpIcRootJnt + '.jointOrientZ'))
                cmds.delete(cmds.aimConstraint(lidUpTargetLocList[0], lidInCSkinRootJnt, offset=(0, 0, 0), weight=1,
                                               aimVector=aimVec,
                                               upVector=UpVec,
                                               worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                               worldUpObject=(self.lidUpMRootJnt),
                                               n=lidInCSkinRootJnt.replace('_jnt', '_aim')))
                cmds.makeIdentity(lidInCSkinRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)

                cmds.select(cl=True)
                lidInCSkinEndJnt = cmds.joint(n=self.judge_LR + '%sUpLidSkinEnd0_jnt' % self.name,
                                              p=cmds.xform(lidUpTargetLocList[0], q=True, ws=True, t=True))
                cmds.parent(lidInCSkinEndJnt, lidInCSkinRootJnt)
                cmds.setAttr(lidInCSkinEndJnt + '.radius', 0.1)

                cmds.aimConstraint(lidUpTargetLocList[0], lidInCSkinRootJnt, offset=(0, 0, 0), weight=1,
                                   aimVector=aimVec,
                                   upVector=UpVec,
                                   worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                   worldUpObject=(self.lidUpMRootJnt), n=lidInCSkinRootJnt.replace('_jnt', '_aim'))

                cmds.select(cl=True)
                lidOutCSkinRootJnt = cmds.joint(
                    n=self.judge_LR + '%sUpLidSkinRoot%s_jnt' % (self.name, len(lidUpTargetLocList) - 1),
                    p=cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True, ws=True, t=True))
                cmds.setAttr(lidOutCSkinRootJnt + '.drawStyle', 2)

                cmds.delete(cmds.aimConstraint(lidUpTargetLocList[-1], lidOutCSkinRootJnt, offset=(0, 0, 0), weight=1,
                                               aimVector=aimVec,
                                               upVector=UpVec,
                                               worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                               worldUpObject=(self.lidUpMRootJnt),
                                               n=lidOutCSkinRootJnt.replace('_jnt', '_aim')))
                cmds.makeIdentity(lidOutCSkinRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)

                cmds.select(cl=True)
                lidOutCSkinEndJnt = cmds.joint(
                    n=self.judge_LR + '%sUpLidSkinEnd%s_jnt' % (self.name, len(lidUpTargetLocList) - 1),
                    p=cmds.xform(lidUpTargetLocList[-1], q=True, ws=True, t=True))

                cmds.parent(lidOutCSkinEndJnt, lidOutCSkinRootJnt)
                cmds.setAttr(lidOutCSkinEndJnt + '.radius', 0.1)

                cmds.aimConstraint(lidUpTargetLocList[-1], lidOutCSkinRootJnt, offset=(0, 0, 0), weight=1,
                                   aimVector=aimVec,
                                   upVector=UpVec,
                                   worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                   worldUpObject=(self.lidUpMRootJnt),
                                   n=lidOutCSkinRootJnt.replace('_jnt', '_aim'))

                cmds.parent(lidInCSkinRootJnt, lidOutCSkinRootJnt, lidSkinJntsGrp)

                lidUpSkinEndJntsList.insert(0, lidInCSkinEndJnt)
                lidUpSkinEndJntsList.insert(len(lidUpSkinEndJntsList), lidOutCSkinEndJnt)

                lidUpSkinJntsList.insert(0, lidInCSkinRootJnt)
                lidUpSkinJntsList.insert(len(lidUpSkinJntsList), lidOutCSkinRootJnt)

                for i, duplidUpSkinJnts in enumerate(duplidUpSkinJntsList):
                    duplidUpOct = cmds.orientConstraint(duplidUpOrgList[i], duplidLowOrgList[i], duplidUpSkinJnts,
                                                        offset=(0, 0, 0), weight=1,
                                                        n=self.set_LR + '_' + '%sUpConstructor%s_oct' % (
                                                            self.name, str(i + 1).zfill(2)))
                    cmds.setAttr(duplidUpOct[0] + '.interpType', 2)
                    duplidUpOctList.append(duplidUpOct[0])

                    duplidLowOct = cmds.orientConstraint(duplidLowOrgList[i], duplidUpOrgList[i],
                                                         duplidLowSkinJntsList[i],
                                                         offset=(0, 0, 0),
                                                         weight=1,
                                                         n=self.set_LR + '_' + '%sLowConstructor%s_oct' % (
                                                             self.name, str(i + 1).zfill(2)))
                    cmds.setAttr(duplidLowOct[0] + '.interpType', 2)
                    duplidLowOctList.append(duplidLowOct[0])
                cmds.select(cl=True)

                duplidBlinkRvs = cmds.createNode('reverse', n=self.set_LR + '_' + '%slidBlink_rvs' % self.name)
                duplidUpSRmv = cmds.createNode('remapValue', n=self.set_LR + '_' + '%sUpLidStart_rmv' % self.name)
                duplidUpERmv = cmds.createNode('remapValue', n=self.set_LR + '_' + '%sUpLidEnd_rmv' % self.name)
                duplidLowSRmv = cmds.createNode('remapValue', n=self.set_LR + '_' + '%sLowLidStart_rmv' % self.name)
                duplidLowERmv = cmds.createNode('remapValue', n=self.set_LR + '_' + '%sLowLidEnd_rmv' % self.name)

                cmds.connectAttr(self.duplicateUpPath[0] + '.blink', duplidUpSRmv + '.inputValue')
                cmds.connectAttr(self.duplicateUpPath[0] + '.blinkSize', duplidUpSRmv + '.outputMax')
                cmds.connectAttr(self.duplicateUpPath[0] + '.blink', duplidUpERmv + '.inputValue')
                cmds.connectAttr(self.duplicateUpPath[0] + '.blinkSize', duplidBlinkRvs + '.inputX')
                cmds.connectAttr(duplidBlinkRvs + '.outputX', duplidUpERmv + '.outputMax')

                cmds.connectAttr(self.duplicateUpPath[0] + '.blink', duplidLowSRmv + '.inputValue')
                cmds.connectAttr(duplidBlinkRvs + '.outputX', duplidLowSRmv + '.outputMax')
                cmds.connectAttr(self.duplicateUpPath[0] + '.blink', duplidLowERmv + '.inputValue')
                cmds.connectAttr(self.duplicateUpPath[0] + '.blinkSize', duplidLowERmv + '.outputMax')

                cmds.setAttr(duplidUpSRmv + '.outputMin', 1)
                cmds.setAttr(duplidLowSRmv + '.outputMin', 1)

                for i, indexUpOct in enumerate(duplidUpOctList):
                    cmds.connectAttr(duplidUpSRmv + '.outValue', indexUpOct + '.' + duplidUpOrgList[i] + 'W0')
                    cmds.connectAttr(duplidUpERmv + '.outValue', indexUpOct + '.' + duplidLowOrgList[i] + 'W1')

                for i, indexLowOct in enumerate(duplidLowOctList):
                    cmds.connectAttr(duplidLowSRmv + '.outValue', indexLowOct + '.' + duplidLowOrgList[i] + 'W0')
                    cmds.connectAttr(duplidLowERmv + '.outValue', indexLowOct + '.' + duplidUpOrgList[i] + 'W1')

                cmds.select(cl=True)
                duplidInCSkinRootJnt = cmds.joint(n=self.set_LR + '_' + '%sUpLidSkinRoot0_jnt' % self.name,
                                                  p=cmds.xform(self.set_LR + '_' + 'eyeBall_jnt', q=True, ws=True,
                                                               t=True))
                cmds.setAttr(duplidInCSkinRootJnt + '.drawStyle', 2)
                cmds.setAttr(duplidInCSkinRootJnt + '.jointOrient',
                             cmds.getAttr(dupSortUpSkinCrvJnts[0] + '.jointOrientX'),
                             cmds.getAttr(dupSortUpSkinCrvJnts[0] + '.jointOrientY'),
                             cmds.getAttr(dupSortUpSkinCrvJnts[0] + '.jointOrientZ'))
                cmds.delete(
                    cmds.aimConstraint(dupLidUpTargetLocList[0], duplidInCSkinRootJnt, offset=(0, 0, 0), weight=1,
                                       aimVector=aimVec,
                                       upVector=UpVec,
                                       worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                       worldUpObject=(dupSortUpSkinCrvJnts[0]),
                                       n=duplidInCSkinRootJnt.replace('_jnt', '_aim')))
                cmds.makeIdentity(duplidInCSkinRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)

                cmds.select(cl=True)
                duplidInCSkinEndJnt = cmds.joint(n=self.set_LR + '_' + '%sUpLidSkinEnd0_jnt' % self.name,
                                                 p=cmds.xform(dupLidUpTargetLocList[0], q=True, ws=True, t=True))
                cmds.parent(duplidInCSkinEndJnt, duplidInCSkinRootJnt)
                cmds.setAttr(duplidInCSkinEndJnt + '.radius', 0.1)

                cmds.aimConstraint(dupLidUpTargetLocList[0], duplidInCSkinRootJnt, offset=(0, 0, 0), weight=1,
                                   aimVector=aimVec,
                                   upVector=UpVec,
                                   worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                   worldUpObject=(dupSortUpSkinCrvJnts[0]),
                                   n=duplidInCSkinRootJnt.replace('_jnt', '_aim'))

                cmds.select(cl=True)
                duplidOutCSkinRootJnt = cmds.joint(
                    n=self.set_LR + '_' + '%sUpLidSkinRoot%s_jnt' % (self.name, len(dupLidUpTargetLocList) - 1),
                    p=cmds.xform(self.set_LR + '_' + 'eyeBall_jnt', q=True, ws=True, t=True))
                cmds.setAttr(duplidOutCSkinRootJnt + '.drawStyle', 2)

                cmds.delete(
                    cmds.aimConstraint(dupLidUpTargetLocList[-1], duplidOutCSkinRootJnt, offset=(0, 0, 0), weight=1,
                                       aimVector=aimVec,
                                       upVector=UpVec,
                                       worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                       worldUpObject=(dupSortUpSkinCrvJnts[0]),
                                       n=duplidOutCSkinRootJnt.replace('_jnt', '_aim')))
                cmds.makeIdentity(duplidOutCSkinRootJnt, apply=True, t=0, r=1, s=0, n=0, pn=1)

                cmds.select(cl=True)
                duplidOutCSkinEndJnt = cmds.joint(
                    n=self.set_LR + '_' + '%sUpLidSkinEnd%s_jnt' % (self.name, len(dupLidUpTargetLocList) - 1),
                    p=cmds.xform(dupLidUpTargetLocList[-1], q=True, ws=True, t=True))

                cmds.parent(duplidOutCSkinEndJnt, duplidOutCSkinRootJnt)
                cmds.setAttr(duplidOutCSkinEndJnt + '.radius', 0.1)

                cmds.aimConstraint(dupLidUpTargetLocList[-1], duplidOutCSkinRootJnt, offset=(0, 0, 0), weight=1,
                                   aimVector=aimVec,
                                   upVector=UpVec,
                                   worldUpType=('objectrotation'), worldUpVector=(1, 0, 0),
                                   worldUpObject=(dupSortUpSkinCrvJnts[0]),
                                   n=lidOutCSkinRootJnt.replace('_jnt', '_aim'))

                cmds.parent(duplidInCSkinRootJnt, duplidOutCSkinRootJnt, dupLidSkinJntsGrp)

                duplidUpSkinEndJntsList.insert(0, duplidInCSkinEndJnt)
                duplidUpSkinEndJntsList.insert(len(duplidUpSkinEndJntsList), duplidOutCSkinEndJnt)

                duplidUpSkinJntsList.insert(0, duplidInCSkinRootJnt)
                duplidUpSkinJntsList.insert(len(duplidUpSkinJntsList), duplidOutCSkinRootJnt)

                # skinVtxList -------------------------------------------------

                msel = api.MSelectionList()
                msel.add(self.polyObject)
                dag = msel.getDagPath(0)
                MFn_mesh = api.MFnMesh(dag)
                MIt_mesh = api.MItMeshVertex(dag)

                self.lidUpSortVtxIdList = []
                for i, index in enumerate(self.lidInnerUpList):
                    oldVtxList = []
                    cmds.select(self.polyObject + '.vtx[%s]' % index,
                                self.polyObject + '.vtx[%s]' % self.lidOuterUpList[i], r=True)
                    cmds.SelectEdgeLoopSp()
                    oldSel = cmds.ls(sl=True, fl=True)
                    for oldIn in oldSel:
                        cmds.select(oldIn, r=True)
                        Mglobal = api.MGlobal.getRichSelection()
                        richSel = api.MRichSelection(Mglobal)
                        getSelection = richSel.getSelection()
                        getComponent = getSelection.getComponent(0)
                        MFnSingle = api.MFnSingleIndexedComponent(getComponent[1])
                        elenemt = MFnSingle.getElements()
                        oldVtxList.append(elenemt[0])

                    sortVtxID = []
                    for i2 in range(len(oldVtxList)):
                        if i2 == 0:
                            sortVtxID.append(self.lidInnerUpList[i])
                            MIt_mesh.setIndex(self.lidInnerUpList[i])
                            continue
                        getSkinVtxList = MIt_mesh.getConnectedVertices()
                        for getIn2 in getSkinVtxList:
                            if getIn2 in oldVtxList and not getIn2 in sortVtxID:
                                sortVtxID.append(getIn2)
                                MIt_mesh.setIndex(getIn2)
                    self.lidUpSortVtxIdList.append(sortVtxID)

                self.lidLowSortVtxIdList = []
                for i, index in enumerate(self.lidInnerLowList):
                    oldVtxList = []
                    cmds.select(self.polyObject + '.vtx[%s]' % index,
                                self.polyObject + '.vtx[%s]' % self.lidOuterLowList[i], r=True)
                    cmds.SelectEdgeLoopSp()
                    oldSel = cmds.ls(sl=True, fl=True)
                    for oldIn in oldSel:
                        cmds.select(oldIn, r=True)
                        Mglobal = api.MGlobal.getRichSelection()
                        richSel = api.MRichSelection(Mglobal)
                        getSelection = richSel.getSelection()
                        getComponent = getSelection.getComponent(0)
                        MFnSingle = api.MFnSingleIndexedComponent(getComponent[1])
                        elenemt = MFnSingle.getElements()
                        oldVtxList.append(elenemt[0])

                    sortVtxID = []
                    for i2 in range(len(oldVtxList)):
                        if i2 == 0:
                            sortVtxID.append(self.lidInnerLowList[i])
                            MIt_mesh.setIndex(self.lidInnerLowList[i])
                            continue
                        getSkinVtxList = MIt_mesh.getConnectedVertices()
                        for getIn2 in getSkinVtxList:
                            if getIn2 in oldVtxList and not getIn2 in sortVtxID:
                                sortVtxID.append(getIn2)
                                MIt_mesh.setIndex(getIn2)
                    self.lidLowSortVtxIdList.append(sortVtxID)
                cmds.select(cl=True)


                lidUpPoint = api.MPoint(cmds.xform(self.upLidCrvPointList[3], q=True, ws=True, t=True))
                lidLowPoint = api.MPoint(cmds.xform(self.LowLidCrvPointList[3], q=True, ws=True, t=True))
                distance = lidUpPoint.distanceTo(lidLowPoint)
                alignList = ['In', 'Mid', 'Out']
                XYZList = ['X', 'Y', 'Z']
                RGBList = ['R', 'G', 'B']
                ctlsSize = (cmds.getAttr(self.upLidCrvPointList[3] + '.tz') * 0.2)

                if self.judge_LR == 'l_':
                    tzOffset = ctlsSize / 2

                    lidUpRoot_ctl = cmds.circle(c=(0, 0, tzOffset), nr=(0, 0, 1), sw=360, r=ctlsSize,
                                                d=3, ut=0, tol=0.01, s=8, ch=False,
                                                n='l_' + self.name + 'UpRoot_ctl')
                    lidUpRootCtlGrp = cmds.group(lidUpRoot_ctl, n='l_' + self.name + 'UpRootCtl_grp')
                    for Cvs in range(4, 7):
                        cmds.xform(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, ws=True, t=(
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[0], 4),
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[3]', w=True)[1], 4),
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[2], 4)
                        ))
                    cmds.xform(lidUpRootCtlGrp, ws=True,
                               t=cmds.xform(self.upLidCrvPointList[3], q=True, ws=True, t=True))
                    cmds.transformLimits(lidUpRoot_ctl[0], ty=(-1, 1), ety=(0, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], ty=(-1, 1), ety=(1, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], tz=(-1, 1), etx=(0, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], tz=(-1, 1), etx=(1, 1))
                    cmds.setAttr(lidUpRootCtlGrp + '.s', distance, distance, distance)

                    lidUpTYMdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'UpTY_mdi')
                    lidUpTYPma = cmds.createNode('plusMinusAverage', n='l_' + self.name + 'UpTY_pma')
                    lidUpTXPma = cmds.createNode('plusMinusAverage', n='l_' + self.name + 'UpTX_pma')
                    lidUpRZ45Mdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'Up45RZ_mdi')
                    cmds.setAttr(lidUpRZ45Mdi + '.input2X', -45)
                    cmds.setAttr(lidUpRZ45Mdi + '.input2Z', 45)
                    cmds.setAttr(lidUpRZ45Mdi + '.operation', 2)
                    lidUpRZMdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'UpRZ_mdi')
                    lidUpTXMdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'UpTX_mdi')
                    cmds.setAttr(lidUpTXMdi + '.input2X', 10)
                    cmds.setAttr(lidUpTXMdi + '.input2Y', 20)

                    for i, AL in enumerate(alignList):
                        cmds.setAttr(lidUpTYMdi + '.input2%s' % XYZList[i],
                                     cmds.getAttr(
                                         'l_' + self.name + '%sUpRoot_jnt.jointOrientX' % AL) + cmds.getAttr(
                                         'l_' + self.name + '%sLowRoot_jnt.jointOrientX' % AL))
                        cmds.connectAttr(lidUpRoot_ctl[0] + '.translateY', lidUpTYMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpTYMdi + '.output%s' % XYZList[i],
                                         lidUpTYPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTYPma + '.output3D%s' % XYZList[i].lower(),
                                         'l_' + self.name + '%sUpRoot_jnt.rotateX' % AL)

                        if i == 1:
                            cmds.connectAttr(lidUpTXMdi + '.outputY',
                                             lidUpTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                            cmds.connectAttr(lidUpTXPma + '.output3D%s' % XYZList[i].lower(),
                                             'l_' + self.name + '%sUpRoot_jnt.rotateY' % AL)
                            continue
                        cmds.setAttr(lidUpRZMdi + '.input2%s' % XYZList[i],
                                     cmds.getAttr(
                                         'l_' + self.name + '%sUpRoot_jnt.jointOrientX' % AL) + cmds.getAttr(
                                         'l_' + self.name + '%sLowRoot_jnt.jointOrientX' % AL))
                        cmds.connectAttr(lidUpRoot_ctl[0] + '.rotateZ', lidUpRZ45Mdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpRZ45Mdi + '.output%s' % XYZList[i], lidUpRZMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpRZMdi + '.output%s' % XYZList[i],
                                         lidUpTYPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTXMdi + '.outputX',
                                         lidUpTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTXPma + '.output3D%s' % XYZList[i].lower(),
                                         'l_' + self.name + '%sUpRoot_jnt.rotateY' % AL)

                    cmds.connectAttr(lidUpRoot_ctl[0] + '.translateX', lidUpTXMdi + '.input1X')
                    cmds.connectAttr(lidUpRoot_ctl[0] + '.translateX', lidUpTXMdi + '.input1Y')

                    lidLowRoot_ctl = cmds.circle(c=(0, 0, tzOffset), nr=(0, 0, 1), sw=360, r=ctlsSize,
                                                 d=3, ut=0, tol=0.01, s=8, ch=False,
                                                 n='l_' + self.name + 'LowRoot_ctl')
                    lidLowRootCtlGrp = cmds.group(lidLowRoot_ctl, n='l_' + self.name + 'LowRootCtl_grp')
                    for Cvs in range(4, 7):
                        cmds.xform(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, ws=True, t=(
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[0], 4),
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[3]', w=True)[1], 4),
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[2], 4)
                        ))
                    cmds.xform(lidLowRootCtlGrp, ws=True,
                               t=cmds.xform('l_' + self.name + 'MidLowSpace_jnt', q=True, ws=True, t=True))
                    cmds.transformLimits(lidLowRoot_ctl[0], ty=(-1, 1), ety=(0, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], ty=(-1, 1), ety=(1, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], tz=(-1, 1), etx=(0, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], tz=(-1, 1), etx=(1, 1))
                    cmds.setAttr(lidLowRootCtlGrp + '.s', distance, -distance, distance)

                    lidLowTYPma = cmds.createNode('plusMinusAverage', n='l_' + self.name + 'LowTY_pma')
                    lidLowTYRTPma = cmds.createNode('plusMinusAverage', n='l_' + self.name + 'LowTYRT_pma')
                    lidLowRZ45Mdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'Low45RZ_mdi')
                    cmds.setAttr(lidLowRZ45Mdi + '.input2X', -45)
                    cmds.setAttr(lidLowRZ45Mdi + '.input2Z', 45)
                    cmds.setAttr(lidLowRZ45Mdi + '.operation', 2)
                    lidLowTYMdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'LowTY_mdi')
                    lidLowTYMinMdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'LowTYMin_mdi')
                    cmds.setAttr(lidLowTYMinMdi + '.input2', -1, -1, -1)
                    lidLowOutBcl = cmds.createNode('blendColors', n='l_' + self.name + 'LowOut_bcl')
                    cmds.setAttr(lidLowOutBcl + '.blender', 1)

                    upToLowPma = cmds.createNode('plusMinusAverage', n='l_' + self.name + 'UpToLow_pma')
                    cmds.connectAttr('l_' + self.name + 'UpRoot_ctl.translateY',
                                     upToLowPma + '.input2D[0].input2Dx')
                    cmds.connectAttr('l_' + self.name + 'UpRoot_ctl.translateY',
                                     upToLowPma + '.input2D[0].input2Dy')
                    cmds.connectAttr(lidUpRZ45Mdi + '.outputX', upToLowPma + '.input2D[1].input2Dx')
                    cmds.connectAttr(lidUpRZ45Mdi + '.outputZ', upToLowPma + '.input2D[1].input2Dy')
                    lidUpToLowTYMinMdi = cmds.createNode('multiplyDivide',
                                                         n='l_' + self.name + 'UpToLowTYMin_mdi')
                    cmds.setAttr(lidUpToLowTYMinMdi + '.input2', -1, -1, -1)
                    cmds.connectAttr(upToLowPma + '.output2Dx', lidUpToLowTYMinMdi + '.input1X')
                    cmds.connectAttr('l_' + self.name + 'UpRoot_ctl.translateY',
                                     lidUpToLowTYMinMdi + '.input1Y')
                    cmds.connectAttr(upToLowPma + '.output2Dy', lidUpToLowTYMinMdi + '.input1Z')
                    lidUpToLowRvs = cmds.createNode('reverse', n='l_' + self.name + 'UpToLow_rvs')
                    lidUpToLowTYPlusMdi = cmds.createNode('multiplyDivide',
                                                          n='l_' + self.name + 'UpToLowTYPlusTY_mdi')
                    lidLowTX = cmds.createNode('multiplyDivide', n='l_' + self.name + 'LowTX_mdi')
                    cmds.setAttr(lidLowTX + '.input2X', -10)
                    cmds.setAttr(lidLowTX + '.input2Y', -20)
                    cmds.connectAttr(lidLowRoot_ctl[0] + '.translateX', lidLowTX + '.input1X')
                    cmds.connectAttr(lidLowRoot_ctl[0] + '.translateX', lidLowTX + '.input1Y')
                    lidLowTXPma = cmds.createNode('plusMinusAverage', n='l_' + self.name + 'LowTX_pma')

                    for i, conIn in enumerate(alignList):
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.translateY',
                                         lidLowTYPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.translateY',
                                         lidLowTYRTPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowTYPma + '.output3D%s' % XYZList[i].lower(),
                                         lidLowTYMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidLowTYRTPma + '.output3D%s' % XYZList[i].lower(),
                                         lidLowTYMinMdi + '.input1%s' % XYZList[i])
                        cmds.setAttr(lidLowTYMdi + '.input2%s' % XYZList[i],
                                     cmds.getAttr('l_' + self.name + '%sUpRoot_jnt.jointOrientX' % conIn) +
                                     cmds.getAttr('l_' + self.name + '%sLowRoot_jnt.jointOrientX' % conIn))

                        outCds = cmds.createNode('condition', n='l_' + self.name + '%sLow_cds' % conIn)
                        cmds.setAttr(outCds + '.operation', 3)
                        cmds.connectAttr(lidLowTYMdi + '.output%s' % XYZList[i], outCds + '.colorIfTrueR')
                        cmds.connectAttr(lidLowTYMinMdi + '.output%s' % XYZList[i], outCds + '.secondTerm')
                        cmds.connectAttr(outCds + '.outColorR', lidLowOutBcl + '.color1%s' % RGBList[i])
                        cmds.connectAttr(lidLowTYMdi + '.output%s' % XYZList[i],
                                         lidLowOutBcl + '.color2%s' % RGBList[i])

                        cmds.connectAttr(lidLowOutBcl + '.output%s' % RGBList[i],
                                         'l_' + self.name + '%sLowRoot_jnt.rotateX' % conIn)
                        cmds.connectAttr(lidUpToLowTYMinMdi + '.output%s' % XYZList[i],
                                         lidUpToLowRvs + '.input%s' % XYZList[i])
                        cmds.connectAttr(lidUpToLowRvs + '.output%s' % XYZList[i],
                                         lidUpToLowTYPlusMdi + '.input1%s' % XYZList[i])
                        cmds.setAttr(lidUpToLowTYPlusMdi + '.input2%s' % XYZList[i],
                                     -(cmds.getAttr(
                                         'l_' + self.name + '%sUpRoot_jnt.jointOrientX' % conIn) + cmds.getAttr(
                                         'l_' + self.name + '%sLowRoot_jnt.jointOrientX' % conIn)))
                        cmds.connectAttr(lidUpToLowRvs + '.output%s' % XYZList[i], outCds + '.firstTerm')
                        cmds.connectAttr(lidUpToLowTYPlusMdi + '.output%s' % XYZList[i], outCds + '.colorIfFalseR')
                        cmds.connectAttr(lidLowTX + '.outputX',
                                         lidLowTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowTXPma + '.output3D%s' % XYZList[i].lower(),
                                         'l_' + self.name + '%sLowRoot_jnt.rotateY' % conIn)

                        if i == 1:
                            continue
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.rotateZ', lidLowRZ45Mdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidLowRZ45Mdi + '.output%s' % XYZList[i],
                                         lidLowTYPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowRZ45Mdi + '.output%s' % XYZList[i],
                                         lidLowTYRTPma + '.input3D[1].input3D%s' % XYZList[i].lower())





                    lidUpRoot_ctl = cmds.circle(c=(0, 0, tzOffset), nr=(0, 0, 1), sw=360, r=ctlsSize,
                                                d=3, ut=0, tol=0.01, s=8, ch=False,
                                                n='r_' + self.name + 'UpRoot_ctl')
                    lidUpRootCtlGrp = cmds.group(lidUpRoot_ctl, n='r_' + self.name + 'UpRootCtl_grp')
                    for Cvs in range(4, 7):
                        cmds.xform(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, ws=True, t=(
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[0], 4),
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[3]', w=True)[1], 4),
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[2], 4)
                        ))
                    cmds.xform(lidUpRootCtlGrp, ws=True,
                               t=(-(cmds.xform(self.upLidCrvPointList[3], q=True, ws=True, t=True)[0]),
                                  (cmds.xform(self.upLidCrvPointList[3], q=True, ws=True, t=True)[1]),
                                  (cmds.xform(self.upLidCrvPointList[3], q=True, ws=True, t=True)[2])))
                    cmds.transformLimits(lidUpRoot_ctl[0], ty=(-1, 1), ety=(0, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], ty=(-1, 1), ety=(1, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], tz=(-1, 1), etx=(0, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], tz=(-1, 1), etx=(1, 1))
                    cmds.setAttr(lidUpRootCtlGrp + '.s', -distance, distance, distance)


                    lidUpTYMdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'UpTY_mdi')
                    lidUpTYPma = cmds.createNode('plusMinusAverage', n='r_' + self.name + 'UpTY_pma')
                    lidUpTXPma = cmds.createNode('plusMinusAverage', n='r_' + self.name + 'UpTX_pma')
                    lidUpRZ45Mdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'Up45RZ_mdi')
                    cmds.setAttr(lidUpRZ45Mdi + '.input2X', -45)
                    cmds.setAttr(lidUpRZ45Mdi + '.input2Z', 45)
                    cmds.setAttr(lidUpRZ45Mdi + '.operation', 2)
                    lidUpRZMdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'UpRZ_mdi')
                    lidUpTXMdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'UpTX_mdi')
                    cmds.setAttr(lidUpTXMdi + '.input2X', 10)
                    cmds.setAttr(lidUpTXMdi + '.input2Y', 20)

                    for i, AL in enumerate(alignList):

                        rotLoc = cmds.spaceLocator()
                        grp = cmds.group(rotLoc)
                        cmds.parentConstraint('r_' + self.name + '%sLowRoot_jnt' % AL, grp)
                        cmds.parentConstraint('r_' + self.name + '%sUpRoot_jnt' % AL, rotLoc[0])

                        cmds.setAttr(lidUpTYMdi + '.input2%s' % XYZList[i], cmds.getAttr(rotLoc[0] + '.rx'))

                        cmds.connectAttr(lidUpRoot_ctl[0] + '.translateY', lidUpTYMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpTYMdi + '.output%s' % XYZList[i],
                                         lidUpTYPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTYPma + '.output3D%s' % XYZList[i].lower(),
                                         'r_' + self.name + '%sUpRoot_jnt.rotateX' % AL)

                        if i == 1:
                            cmds.connectAttr(lidUpTXMdi + '.outputY',
                                             lidUpTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                            cmds.connectAttr(lidUpTXPma + '.output3D%s' % XYZList[i].lower(),
                                             'r_' + self.name + '%sUpRoot_jnt.rotateY' % AL)
                            cmds.delete(grp)
                            continue
                        cmds.setAttr(lidUpRZMdi + '.input2%s' % XYZList[i], cmds.getAttr(rotLoc[0] + '.rx'))
                        cmds.connectAttr(lidUpRoot_ctl[0] + '.rotateZ', lidUpRZ45Mdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpRZ45Mdi + '.output%s' % XYZList[i], lidUpRZMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpRZMdi + '.output%s' % XYZList[i],
                                         lidUpTYPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTXMdi + '.outputX',
                                         lidUpTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTXPma + '.output3D%s' % XYZList[i].lower(),
                                         'r_' + self.name + '%sUpRoot_jnt.rotateY' % AL)

                        cmds.delete(grp)

                    cmds.connectAttr(lidUpRoot_ctl[0] + '.translateX', lidUpTXMdi + '.input1X')
                    cmds.connectAttr(lidUpRoot_ctl[0] + '.translateX', lidUpTXMdi + '.input1Y')




                    lidLowRoot_ctl = cmds.circle(c=(0, 0, tzOffset), nr=(0, 0, 1), sw=360, r=ctlsSize,
                                                 d=3, ut=0, tol=0.01, s=8, ch=False,
                                                 n='r_' + self.name + 'LowRoot_ctl')
                    lidLowRootCtlGrp = cmds.group(lidLowRoot_ctl, n='r_' + self.name + 'LowRootCtl_grp')
                    for Cvs in range(4, 7):
                        cmds.xform(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, ws=True, t=(
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[0], 4),
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[3]', w=True)[1], 4),
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[2], 4)
                        ))
                    cmds.xform(lidLowRootCtlGrp, ws=True,
                               t=(cmds.xform('r_' + self.name + 'MidLowSpace_jnt', q=True, ws=True, t=True)))
                    cmds.transformLimits(lidLowRoot_ctl[0], ty=(-1, 1), ety=(0, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], ty=(-1, 1), ety=(1, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], tz=(-1, 1), etx=(0, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], tz=(-1, 1), etx=(1, 1))
                    cmds.setAttr(lidLowRootCtlGrp + '.s', -distance, -distance, distance)

                    lidLowTYPma = cmds.createNode('plusMinusAverage', n='r_' + self.name + 'LowTY_pma')
                    lidLowTYRTPma = cmds.createNode('plusMinusAverage', n='r_' + self.name + 'LowTYRT_pma')
                    lidLowRZ45Mdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'Low45RZ_mdi')
                    cmds.setAttr(lidLowRZ45Mdi + '.input2X', -45)
                    cmds.setAttr(lidLowRZ45Mdi + '.input2Z', 45)
                    cmds.setAttr(lidLowRZ45Mdi + '.operation', 2)
                    lidLowTYMdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'LowTY_mdi')
                    lidLowTYMinMdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'LowTYMin_mdi')
                    cmds.setAttr(lidLowTYMinMdi + '.input2', -1, -1, -1)
                    lidLowOutBcl = cmds.createNode('blendColors', n='r_' + self.name + 'LowOut_bcl')
                    cmds.setAttr(lidLowOutBcl + '.blender', 1)

                    upToLowPma = cmds.createNode('plusMinusAverage', n='r_' + self.name + 'UpToLow_pma')
                    cmds.connectAttr('r_' + self.name + 'UpRoot_ctl.translateY',
                                     upToLowPma + '.input2D[0].input2Dx')
                    cmds.connectAttr('r_' + self.name + 'UpRoot_ctl.translateY',
                                     upToLowPma + '.input2D[0].input2Dy')
                    cmds.connectAttr(lidUpRZ45Mdi + '.outputX', upToLowPma + '.input2D[1].input2Dx')
                    cmds.connectAttr(lidUpRZ45Mdi + '.outputZ', upToLowPma + '.input2D[1].input2Dy')
                    lidUpToLowTYMinMdi = cmds.createNode('multiplyDivide',
                                                         n='r_' + self.name + 'UpToLowTYMin_mdi')
                    cmds.setAttr(lidUpToLowTYMinMdi + '.input2', -1, -1, -1)
                    cmds.connectAttr(upToLowPma + '.output2Dx', lidUpToLowTYMinMdi + '.input1X')
                    cmds.connectAttr('r_' + self.name + 'UpRoot_ctl.translateY',
                                     lidUpToLowTYMinMdi + '.input1Y')
                    cmds.connectAttr(upToLowPma + '.output2Dy', lidUpToLowTYMinMdi + '.input1Z')
                    lidUpToLowRvs = cmds.createNode('reverse', n='r_' + self.name + 'UpToLow_rvs')
                    lidUpToLowTYPlusMdi = cmds.createNode('multiplyDivide',
                                                          n='r_' + self.name + 'UpToLowTYPlus_mdi')
                    lidLowTX = cmds.createNode('multiplyDivide', n='r_' + self.name + 'LowTX_mdi')
                    cmds.setAttr(lidLowTX + '.input2X', -10)
                    cmds.setAttr(lidLowTX + '.input2Y', -20)
                    cmds.connectAttr(lidLowRoot_ctl[0] + '.translateX', lidLowTX + '.input1X')
                    cmds.connectAttr(lidLowRoot_ctl[0] + '.translateX', lidLowTX + '.input1Y')
                    lidLowTXPma = cmds.createNode('plusMinusAverage', n='r_' + self.name + 'LowTX_pma')

                    for i, conIn in enumerate(alignList):
                        rotLoc = cmds.spaceLocator()
                        grp = cmds.group(rotLoc)
                        cmds.parentConstraint('r_' + self.name + '%sLowRoot_jnt' % conIn, grp)
                        cmds.parentConstraint('r_' + self.name + '%sUpRoot_jnt' % conIn, rotLoc[0])

                        cmds.connectAttr(lidLowRoot_ctl[0] + '.translateY',
                                         lidLowTYPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.translateY',
                                         lidLowTYRTPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowTYPma + '.output3D%s' % XYZList[i].lower(),
                                         lidLowTYMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidLowTYRTPma + '.output3D%s' % XYZList[i].lower(),
                                         lidLowTYMinMdi + '.input1%s' % XYZList[i])
                        cmds.setAttr(lidLowTYMdi + '.input2%s' % XYZList[i], cmds.getAttr(rotLoc[0] + '.rx'))

                        outCds = cmds.createNode('condition', n='r_' + self.name + '%sLow_cds' % conIn)
                        cmds.setAttr(outCds + '.operation', 3)
                        cmds.connectAttr(lidLowTYMdi + '.output%s' % XYZList[i], outCds + '.colorIfTrueR')
                        cmds.connectAttr(lidLowTYMinMdi + '.output%s' % XYZList[i], outCds + '.secondTerm')
                        cmds.connectAttr(outCds + '.outColorR', lidLowOutBcl + '.color1%s' % RGBList[i])
                        cmds.connectAttr(lidLowTYMdi + '.output%s' % XYZList[i],
                                         lidLowOutBcl + '.color2%s' % RGBList[i])

                        cmds.connectAttr(lidLowOutBcl + '.output%s' % RGBList[i],
                                         'r_' + self.name + '%sLowRoot_jnt.rotateX' % conIn)
                        cmds.connectAttr(lidUpToLowTYMinMdi + '.output%s' % XYZList[i],
                                         lidUpToLowRvs + '.input%s' % XYZList[i])
                        cmds.connectAttr(lidUpToLowRvs + '.output%s' % XYZList[i],
                                         lidUpToLowTYPlusMdi + '.input1%s' % XYZList[i])
                        cmds.setAttr(lidUpToLowTYPlusMdi + '.input2%s' % XYZList[i], -cmds.getAttr(rotLoc[0] + '.rx'))
                        cmds.connectAttr(lidUpToLowRvs + '.output%s' % XYZList[i], outCds + '.firstTerm')
                        cmds.connectAttr(lidUpToLowTYPlusMdi + '.output%s' % XYZList[i], outCds + '.colorIfFalseR')
                        cmds.connectAttr(lidLowTX + '.outputX',
                                         lidLowTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowTXPma + '.output3D%s' % XYZList[i].lower(),
                                         'r_' + self.name + '%sLowRoot_jnt.rotateY' % conIn)

                        if i == 1:
                            cmds.delete(grp)
                            continue
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.rotateZ', lidLowRZ45Mdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidLowRZ45Mdi + '.output%s' % XYZList[i],
                                         lidLowTYPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowRZ45Mdi + '.output%s' % XYZList[i],
                                         lidLowTYRTPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.delete(grp)









                elif self.judge_LR == 'r_':
                    tzOffset = -(ctlsSize / 2)

                    lidUpRoot_ctl = cmds.circle(c=(0, 0, tzOffset), nr=(0, 0, 1), sw=360, r=ctlsSize,
                                                d=3, ut=0, tol=0.01, s=8, ch=False,
                                                n='r_' + self.name + 'UpRoot_ctl')
                    lidUpRootCtlGrp = cmds.group(lidUpRoot_ctl, n='r_' + self.name + 'UpRootCtl_grp')
                    for Cvs in range(0, 3):
                        cmds.xform(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, ws=True, t=(
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[0], 4),
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[3]', w=True)[1], 4),
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[2], 4)
                        ))
                    cmds.xform(lidUpRootCtlGrp, ws=True,
                               t=cmds.xform(self.upLidCrvPointList[3], q=True, ws=True, t=True))
                    cmds.transformLimits(lidUpRoot_ctl[0], ty=(-1, 1), ety=(0, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], ty=(-1, 1), ety=(1, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], tz=(-1, 1), etx=(0, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], tz=(-1, 1), etx=(1, 1))
                    cmds.setAttr(lidUpRootCtlGrp + '.s', -distance, distance, distance)

                    lidUpTYMdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'UpTY_mdi')
                    lidUpTYPma = cmds.createNode('plusMinusAverage', n='r_' + self.name + 'UpTY_pma')
                    lidUpTXPma = cmds.createNode('plusMinusAverage', n='r_' + self.name + 'UpTX_pma')
                    lidUpRZ45Mdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'Up45RZ_mdi')
                    cmds.setAttr(lidUpRZ45Mdi + '.input2X', -45)
                    cmds.setAttr(lidUpRZ45Mdi + '.input2Z', 45)
                    cmds.setAttr(lidUpRZ45Mdi + '.operation', 2)
                    lidUpRZMdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'UpRZ_mdi')
                    lidUpTXMdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'UpTX_mdi')
                    cmds.setAttr(lidUpTXMdi + '.input2X', 10)
                    cmds.setAttr(lidUpTXMdi + '.input2Y', 20)

                    for i, AL in enumerate(alignList):

                        rotLoc = cmds.spaceLocator()
                        grp = cmds.group(rotLoc)
                        cmds.parentConstraint('r_' + self.name + '%sLowRoot_jnt' % AL, grp)
                        cmds.parentConstraint('r_' + self.name + '%sUpRoot_jnt' % AL, rotLoc[0])

                        cmds.setAttr(lidUpTYMdi + '.input2%s' % XYZList[i], cmds.getAttr(rotLoc[0] + '.rx'))

                        cmds.connectAttr(lidUpRoot_ctl[0] + '.translateY', lidUpTYMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpTYMdi + '.output%s' % XYZList[i],
                                         lidUpTYPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTYPma + '.output3D%s' % XYZList[i].lower(),
                                         'r_' + self.name + '%sUpRoot_jnt.rotateX' % AL)

                        if i == 1:
                            cmds.connectAttr(lidUpTXMdi + '.outputY',
                                             lidUpTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                            cmds.connectAttr(lidUpTXPma + '.output3D%s' % XYZList[i].lower(),
                                             'r_' + self.name + '%sUpRoot_jnt.rotateY' % AL)
                            cmds.delete(grp)
                            continue
                        cmds.setAttr(lidUpRZMdi + '.input2%s' % XYZList[i], cmds.getAttr(rotLoc[0] + '.rx'))
                        cmds.connectAttr(lidUpRoot_ctl[0] + '.rotateZ', lidUpRZ45Mdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpRZ45Mdi + '.output%s' % XYZList[i], lidUpRZMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpRZMdi + '.output%s' % XYZList[i],
                                         lidUpTYPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTXMdi + '.outputX',
                                         lidUpTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTXPma + '.output3D%s' % XYZList[i].lower(),
                                         'r_' + self.name + '%sUpRoot_jnt.rotateY' % AL)

                        cmds.delete(grp)

                    cmds.connectAttr(lidUpRoot_ctl[0] + '.translateX', lidUpTXMdi + '.input1X')
                    cmds.connectAttr(lidUpRoot_ctl[0] + '.translateX', lidUpTXMdi + '.input1Y')

                    lidLowRoot_ctl = cmds.circle(c=(0, 0, tzOffset), nr=(0, 0, 1), sw=360, r=ctlsSize,
                                                 d=3, ut=0, tol=0.01, s=8, ch=False,
                                                 n='r_' + self.name + 'LowRoot_ctl')
                    lidLowRootCtlGrp = cmds.group(lidLowRoot_ctl, n='r_' + self.name + 'LowRootCtl_grp')
                    for Cvs in range(0, 3):
                        cmds.xform(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, ws=True, t=(
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[0], 4),
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[3]', w=True)[1], 4),
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[2], 4)
                        ))
                    cmds.xform(lidLowRootCtlGrp, ws=True,
                               t=cmds.xform('r_' + self.name + 'MidLowSpace_jnt', q=True, ws=True, t=True))
                    cmds.transformLimits(lidLowRoot_ctl[0], ty=(-1, 1), ety=(0, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], ty=(-1, 1), ety=(1, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], tz=(-1, 1), etx=(0, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], tz=(-1, 1), etx=(1, 1))
                    cmds.setAttr(lidLowRootCtlGrp + '.s', -distance, -distance, distance)

                    lidLowTYPma = cmds.createNode('plusMinusAverage', n='r_' + self.name + 'LowTY_pma')
                    lidLowTYRTPma = cmds.createNode('plusMinusAverage', n='r_' + self.name + 'LowTYRT_pma')
                    lidLowRZ45Mdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'Low45RZ_mdi')
                    cmds.setAttr(lidLowRZ45Mdi + '.input2X', -45)
                    cmds.setAttr(lidLowRZ45Mdi + '.input2Z', 45)
                    cmds.setAttr(lidLowRZ45Mdi + '.operation', 2)
                    lidLowTYMdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'LowTY_mdi')
                    lidLowTYMinMdi = cmds.createNode('multiplyDivide', n='r_' + self.name + 'LowTYMin_mdi')
                    cmds.setAttr(lidLowTYMinMdi + '.input2', -1, -1, -1)
                    lidLowOutBcl = cmds.createNode('blendColors', n='r_' + self.name + 'LowOut_bcl')
                    cmds.setAttr(lidLowOutBcl + '.blender', 1)

                    upToLowPma = cmds.createNode('plusMinusAverage', n='r_' + self.name + 'UpToLow_pma')
                    cmds.connectAttr('r_' + self.name + 'UpRoot_ctl.translateY',
                                     upToLowPma + '.input2D[0].input2Dx')
                    cmds.connectAttr('r_' + self.name + 'UpRoot_ctl.translateY',
                                     upToLowPma + '.input2D[0].input2Dy')
                    cmds.connectAttr(lidUpRZ45Mdi + '.outputX', upToLowPma + '.input2D[1].input2Dx')
                    cmds.connectAttr(lidUpRZ45Mdi + '.outputZ', upToLowPma + '.input2D[1].input2Dy')
                    lidUpToLowTYMinMdi = cmds.createNode('multiplyDivide',
                                                         n='r_' + self.name + 'UpToLowTYMin_mdi')
                    cmds.setAttr(lidUpToLowTYMinMdi + '.input2', -1, -1, -1)
                    cmds.connectAttr(upToLowPma + '.output2Dx', lidUpToLowTYMinMdi + '.input1X')
                    cmds.connectAttr('r_' + self.name + 'UpRoot_ctl.translateY',
                                     lidUpToLowTYMinMdi + '.input1Y')
                    cmds.connectAttr(upToLowPma + '.output2Dy', lidUpToLowTYMinMdi + '.input1Z')
                    lidUpToLowRvs = cmds.createNode('reverse', n='r_' + self.name + 'UpToLow_rvs')
                    lidUpToLowTYPlusMdi = cmds.createNode('multiplyDivide',
                                                          n='r_' + self.name + 'UpToLowTYPlus_mdi')
                    lidLowTX = cmds.createNode('multiplyDivide', n='r_' + self.name + 'LowTX_mdi')
                    cmds.setAttr(lidLowTX + '.input2X', -10)
                    cmds.setAttr(lidLowTX + '.input2Y', -20)
                    cmds.connectAttr(lidLowRoot_ctl[0] + '.translateX', lidLowTX + '.input1X')
                    cmds.connectAttr(lidLowRoot_ctl[0] + '.translateX', lidLowTX + '.input1Y')
                    lidLowTXPma = cmds.createNode('plusMinusAverage', n='r_' + self.name + 'LowTX_pma')

                    for i, conIn in enumerate(alignList):
                        rotLoc = cmds.spaceLocator()
                        grp = cmds.group(rotLoc)
                        cmds.parentConstraint('r_' + self.name + '%sLowRoot_jnt' % conIn, grp)
                        cmds.parentConstraint('r_' + self.name + '%sUpRoot_jnt' % conIn, rotLoc[0])

                        cmds.connectAttr(lidLowRoot_ctl[0] + '.translateY',
                                         lidLowTYPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.translateY',
                                         lidLowTYRTPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowTYPma + '.output3D%s' % XYZList[i].lower(),
                                         lidLowTYMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidLowTYRTPma + '.output3D%s' % XYZList[i].lower(),
                                         lidLowTYMinMdi + '.input1%s' % XYZList[i])
                        cmds.setAttr(lidLowTYMdi + '.input2%s' % XYZList[i], cmds.getAttr(rotLoc[0] + '.rx'))

                        outCds = cmds.createNode('condition', n='r_' + self.name + '%sLow_cds' % conIn)
                        cmds.setAttr(outCds + '.operation', 3)
                        cmds.connectAttr(lidLowTYMdi + '.output%s' % XYZList[i], outCds + '.colorIfTrueR')
                        cmds.connectAttr(lidLowTYMinMdi + '.output%s' % XYZList[i], outCds + '.secondTerm')
                        cmds.connectAttr(outCds + '.outColorR', lidLowOutBcl + '.color1%s' % RGBList[i])
                        cmds.connectAttr(lidLowTYMdi + '.output%s' % XYZList[i],
                                         lidLowOutBcl + '.color2%s' % RGBList[i])

                        cmds.connectAttr(lidLowOutBcl + '.output%s' % RGBList[i],
                                         'r_' + self.name + '%sLowRoot_jnt.rotateX' % conIn)
                        cmds.connectAttr(lidUpToLowTYMinMdi + '.output%s' % XYZList[i],
                                         lidUpToLowRvs + '.input%s' % XYZList[i])
                        cmds.connectAttr(lidUpToLowRvs + '.output%s' % XYZList[i],
                                         lidUpToLowTYPlusMdi + '.input1%s' % XYZList[i])
                        cmds.setAttr(lidUpToLowTYPlusMdi + '.input2%s' % XYZList[i], -cmds.getAttr(rotLoc[0] + '.rx'))
                        cmds.connectAttr(lidUpToLowRvs + '.output%s' % XYZList[i], outCds + '.firstTerm')
                        cmds.connectAttr(lidUpToLowTYPlusMdi + '.output%s' % XYZList[i], outCds + '.colorIfFalseR')
                        cmds.connectAttr(lidLowTX + '.outputX',
                                         lidLowTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowTXPma + '.output3D%s' % XYZList[i].lower(),
                                         'r_' + self.name + '%sLowRoot_jnt.rotateY' % conIn)

                        if i == 1:
                            cmds.delete(grp)
                            continue
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.rotateZ', lidLowRZ45Mdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidLowRZ45Mdi + '.output%s' % XYZList[i],
                                         lidLowTYPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowRZ45Mdi + '.output%s' % XYZList[i],
                                         lidLowTYRTPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.delete(grp)

                    lidUpRoot_ctl = cmds.circle(c=(0, 0, tzOffset), nr=(0, 0, 1), sw=360, r=ctlsSize,
                                                d=3, ut=0, tol=0.01, s=8, ch=False,
                                                n='l_' + self.name + 'UpRoot_ctl')
                    lidUpRootCtlGrp = cmds.group(lidUpRoot_ctl, n='l_' + self.name + 'UpRootCtl_grp')
                    for Cvs in range(0, 3):
                        cmds.xform(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, ws=True, t=(
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[0], 4),
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[3]', w=True)[1], 4),
                            round(cmds.pointPosition(lidUpRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[2], 4)
                        ))
                    cmds.xform(lidUpRootCtlGrp, ws=True,
                               t=cmds.xform('l_' + self.name + 'MidUpSpace_jnt', q=True, ws=True, t=True))
                    cmds.transformLimits(lidUpRoot_ctl[0], ty=(-1, 1), ety=(0, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], ty=(-1, 1), ety=(1, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], tz=(-1, 1), etx=(0, 1))
                    cmds.transformLimits(lidUpRoot_ctl[0], tz=(-1, 1), etx=(1, 1))
                    cmds.setAttr(lidUpRootCtlGrp + '.s', distance, distance, distance)

                    lidUpTYMdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'UpTY_mdi')
                    lidUpTYPma = cmds.createNode('plusMinusAverage', n='l_' + self.name + 'UpTY_pma')
                    lidUpTXPma = cmds.createNode('plusMinusAverage', n='l_' + self.name + 'UpTX_pma')
                    lidUpRZ45Mdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'Up45RZ_mdi')
                    cmds.setAttr(lidUpRZ45Mdi + '.input2X', -45)
                    cmds.setAttr(lidUpRZ45Mdi + '.input2Z', 45)
                    cmds.setAttr(lidUpRZ45Mdi + '.operation', 2)
                    lidUpRZMdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'UpRZ_mdi')
                    lidUpTXMdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'UpTX_mdi')
                    cmds.setAttr(lidUpTXMdi + '.input2X', 10)
                    cmds.setAttr(lidUpTXMdi + '.input2Y', 20)

                    for i, AL in enumerate(alignList):

                        rotLoc = cmds.spaceLocator()
                        grp = cmds.group(rotLoc)
                        cmds.parentConstraint('l_' + self.name + '%sLowRoot_jnt' % AL, grp)
                        cmds.parentConstraint('l_' + self.name + '%sUpRoot_jnt' % AL, rotLoc[0])

                        cmds.setAttr(lidUpTYMdi + '.input2%s' % XYZList[i], cmds.getAttr(rotLoc[0] + '.rx'))

                        cmds.connectAttr(lidUpRoot_ctl[0] + '.translateY', lidUpTYMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpTYMdi + '.output%s' % XYZList[i],
                                         lidUpTYPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTYPma + '.output3D%s' % XYZList[i].lower(),
                                         'l_' + self.name + '%sUpRoot_jnt.rotateX' % AL)

                        if i == 1:
                            cmds.connectAttr(lidUpTXMdi + '.outputY',
                                             lidUpTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                            cmds.connectAttr(lidUpTXPma + '.output3D%s' % XYZList[i].lower(),
                                             'l_' + self.name + '%sUpRoot_jnt.rotateY' % AL)
                            cmds.delete(grp)
                            continue
                        cmds.setAttr(lidUpRZMdi + '.input2%s' % XYZList[i], cmds.getAttr(rotLoc[0] + '.rx'))
                        cmds.connectAttr(lidUpRoot_ctl[0] + '.rotateZ', lidUpRZ45Mdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpRZ45Mdi + '.output%s' % XYZList[i], lidUpRZMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidUpRZMdi + '.output%s' % XYZList[i],
                                         lidUpTYPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTXMdi + '.outputX',
                                         lidUpTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidUpTXPma + '.output3D%s' % XYZList[i].lower(),
                                         'l_' + self.name + '%sUpRoot_jnt.rotateY' % AL)

                        cmds.delete(grp)

                    cmds.connectAttr(lidUpRoot_ctl[0] + '.translateX', lidUpTXMdi + '.input1X')
                    cmds.connectAttr(lidUpRoot_ctl[0] + '.translateX', lidUpTXMdi + '.input1Y')

                    lidLowRoot_ctl = cmds.circle(c=(0, 0, tzOffset), nr=(0, 0, 1), sw=360, r=ctlsSize,
                                                 d=3, ut=0, tol=0.01, s=8, ch=False,
                                                 n='l_' + self.name + 'LowRoot_ctl')
                    lidLowRootCtlGrp = cmds.group(lidLowRoot_ctl, n='l_' + self.name + 'LowRootCtl_grp')
                    for Cvs in range(0, 3):
                        cmds.xform(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, ws=True, t=(
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[0], 4),
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[3]', w=True)[1], 4),
                            round(cmds.pointPosition(lidLowRoot_ctl[0] + '.cv[%s]' % Cvs, w=True)[2], 4)
                        ))
                    cmds.xform(lidLowRootCtlGrp, ws=True,
                               t=cmds.xform('l_' + self.name + 'MidLowSpace_jnt', q=True, ws=True, t=True))
                    cmds.transformLimits(lidLowRoot_ctl[0], ty=(-1, 1), ety=(0, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], ty=(-1, 1), ety=(1, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], tz=(-1, 1), etx=(0, 1))
                    cmds.transformLimits(lidLowRoot_ctl[0], tz=(-1, 1), etx=(1, 1))
                    cmds.setAttr(lidLowRootCtlGrp + '.s', distance, -distance, distance)

                    lidLowTYPma = cmds.createNode('plusMinusAverage', n='l_' + self.name + 'LowTY_pma')
                    lidLowTYRTPma = cmds.createNode('plusMinusAverage', n='l_' + self.name + 'LowTYRT_pma')
                    lidLowRZ45Mdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'Low45RZ_mdi')
                    cmds.setAttr(lidLowRZ45Mdi + '.input2X', -45)
                    cmds.setAttr(lidLowRZ45Mdi + '.input2Z', 45)
                    cmds.setAttr(lidLowRZ45Mdi + '.operation', 2)
                    lidLowTYMdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'LowTY_mdi')
                    lidLowTYMinMdi = cmds.createNode('multiplyDivide', n='l_' + self.name + 'LowTYMin_mdi')
                    cmds.setAttr(lidLowTYMinMdi + '.input2', -1, -1, -1)
                    lidLowOutBcl = cmds.createNode('blendColors', n='l_' + self.name + 'LowOut_bcl')
                    cmds.setAttr(lidLowOutBcl+'.blender', 1)

                    upToLowPma = cmds.createNode('plusMinusAverage', n='l_' + self.name + 'UpToLow_pma')
                    cmds.connectAttr('l_' + self.name + 'UpRoot_ctl.translateY',
                                     upToLowPma + '.input2D[0].input2Dx')
                    cmds.connectAttr('l_' + self.name + 'UpRoot_ctl.translateY',
                                     upToLowPma + '.input2D[0].input2Dy')
                    cmds.connectAttr(lidUpRZ45Mdi + '.outputX', upToLowPma + '.input2D[1].input2Dx')
                    cmds.connectAttr(lidUpRZ45Mdi + '.outputZ', upToLowPma + '.input2D[1].input2Dy')
                    lidUpToLowTYMinMdi = cmds.createNode('multiplyDivide',
                                                         n='l_' + self.name + 'UpToLowTYMin_mdi')
                    cmds.setAttr(lidUpToLowTYMinMdi + '.input2', -1, -1, -1)
                    cmds.connectAttr(upToLowPma + '.output2Dx', lidUpToLowTYMinMdi + '.input1X')
                    cmds.connectAttr('l_' + self.name + 'UpRoot_ctl.translateY',
                                     lidUpToLowTYMinMdi + '.input1Y')
                    cmds.connectAttr(upToLowPma + '.output2Dy', lidUpToLowTYMinMdi + '.input1Z')
                    lidUpToLowRvs = cmds.createNode('reverse', n='l_' + self.name + 'UpToLow_rvs')
                    lidUpToLowTYPlusMdi = cmds.createNode('multiplyDivide',
                                                          n='l_' + self.name + 'UpToLowTYPlus_mdi')
                    lidLowTX = cmds.createNode('multiplyDivide', n='l_' + self.name + 'LowTX_mdi')
                    cmds.setAttr(lidLowTX + '.input2X', -10)
                    cmds.setAttr(lidLowTX + '.input2Y', -20)
                    cmds.connectAttr(lidLowRoot_ctl[0] + '.translateX', lidLowTX + '.input1X')
                    cmds.connectAttr(lidLowRoot_ctl[0] + '.translateX', lidLowTX + '.input1Y')
                    lidLowTXPma = cmds.createNode('plusMinusAverage', n='l_' + self.name + 'LowTX_pma')

                    for i, conIn in enumerate(alignList):
                        rotLoc = cmds.spaceLocator()
                        grp = cmds.group(rotLoc)
                        cmds.parentConstraint('l_' + self.name + '%sLowRoot_jnt' % conIn, grp)
                        cmds.parentConstraint('l_' + self.name + '%sUpRoot_jnt' % conIn, rotLoc[0])

                        cmds.connectAttr(lidLowRoot_ctl[0] + '.translateY',
                                         lidLowTYPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.translateY',
                                         lidLowTYRTPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowTYPma + '.output3D%s' % XYZList[i].lower(),
                                         lidLowTYMdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidLowTYRTPma + '.output3D%s' % XYZList[i].lower(),
                                         lidLowTYMinMdi + '.input1%s' % XYZList[i])
                        cmds.setAttr(lidLowTYMdi + '.input2%s' % XYZList[i], cmds.getAttr(rotLoc[0] + '.rx'))

                        outCds = cmds.createNode('condition', n='l_' + self.name + '%sLow_cds' % conIn)
                        cmds.setAttr(outCds + '.operation', 3)
                        cmds.connectAttr(lidLowTYMdi + '.output%s' % XYZList[i], outCds + '.colorIfTrueR')
                        cmds.connectAttr(lidLowTYMinMdi + '.output%s' % XYZList[i], outCds + '.secondTerm')
                        cmds.connectAttr(outCds + '.outColorR', lidLowOutBcl + '.color1%s' % RGBList[i])
                        cmds.connectAttr(lidLowTYMdi + '.output%s' % XYZList[i],
                                         lidLowOutBcl + '.color2%s' % RGBList[i])

                        cmds.connectAttr(lidLowOutBcl + '.output%s' % RGBList[i],
                                         'l_' + self.name + '%sLowRoot_jnt.rotateX' % conIn)
                        cmds.connectAttr(lidUpToLowTYMinMdi + '.output%s' % XYZList[i],
                                         lidUpToLowRvs + '.input%s' % XYZList[i])
                        cmds.connectAttr(lidUpToLowRvs + '.output%s' % XYZList[i],
                                         lidUpToLowTYPlusMdi + '.input1%s' % XYZList[i])
                        cmds.setAttr(lidUpToLowTYPlusMdi + '.input2%s' % XYZList[i], -cmds.getAttr(rotLoc[0] + '.rx'))
                        cmds.connectAttr(lidUpToLowRvs + '.output%s' % XYZList[i], outCds + '.firstTerm')
                        cmds.connectAttr(lidUpToLowTYPlusMdi + '.output%s' % XYZList[i], outCds + '.colorIfFalseR')
                        cmds.connectAttr(lidLowTX + '.outputX',
                                         lidLowTXPma + '.input3D[0].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowTXPma + '.output3D%s' % XYZList[i].lower(),
                                         'l_' + self.name + '%sLowRoot_jnt.rotateY' % conIn)

                        if i == 1:
                            cmds.delete(grp)
                            continue
                        cmds.connectAttr(lidLowRoot_ctl[0] + '.rotateZ', lidLowRZ45Mdi + '.input1%s' % XYZList[i])
                        cmds.connectAttr(lidLowRZ45Mdi + '.output%s' % XYZList[i],
                                         lidLowTYPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.connectAttr(lidLowRZ45Mdi + '.output%s' % XYZList[i],
                                         lidLowTYRTPma + '.input3D[1].input3D%s' % XYZList[i].lower())
                        cmds.delete(grp)


                if not 'facialGlobalJnt_grp' in cmds.ls():
                    cmds.select(cl=True)
                    self.facialGlobalJnt = cmds.joint(n='facialGlobal_jnt')
                    facialGlobalJntGrp = cmds.group(self.facialGlobalJnt, n='facialGlobalJnt_grp')
                    cmds.xform(facialGlobalJntGrp, ws=True, t=(0, cmds.xform(self.judge_LR + 'eyeBall_jnt',
                                                                             q=True, ws=True, t=True)[1],
                                                               cmds.xform(self.judge_LR + 'eyeBall_jnt', q=True,
                                                                          ws=True, t=True)[2]))

                self.allSkinVtxList = self.lidUpSortVtxIdList + self.lidLowSortVtxIdList
                self.allSkinJntsList = lidUpSkinEndJntsList + lidLowSkinEndJntsList

                self.dupallSkinJntsList = duplidUpSkinEndJntsList + duplidLowSkinEndJntsList

                self.allSkinWeightList = []
                self.SetNum = 1.0 / len(self.allSkinVtxList[0])
                if not self.name + 'FacialGlobal_sct' in cmds.ls():
                    self.facialGlobalSkin = cmds.skinCluster(self.polyObject, self.facialGlobalJnt,
                                                             self.allSkinJntsList,
                                                             toSelectedBones=True, n=self.name + 'FacialGlobal_sct')
                    cmds.setAttr(self.facialGlobalSkin[0] + '.skinningMethod', 1)
                    cmds.skinPercent(self.facialGlobalSkin[0], self.polyObject, tv=(self.facialGlobalJnt, 1))
                    for i, rootVtxID in enumerate(self.allSkinVtxList):
                        skinWeightList = []
                        for vi, listVtxID in enumerate(rootVtxID):
                            cmds.skinPercent(self.facialGlobalSkin[0], self.polyObject + '.vtx[%s]' % listVtxID,
                                             tv=(self.facialGlobalJnt, 1))
                            getValue = cmds.gradientControlNoAttr(self.gredient, q=True, cvv=True,
                                                                  vap=(self.SetNum * float(vi)))
                            if getValue > 1:
                                getValue = 1
                            skinWeightList.append(getValue)
                        self.allSkinWeightList.append(skinWeightList)
                    cmds.select(cl=True)
                    for i, weightIn in enumerate(self.allSkinWeightList):
                        for ini, getWeights in enumerate(weightIn):
                            cmds.skinPercent(self.facialGlobalSkin[0],
                                             self.polyObject + '.vtx[%s]' % self.allSkinVtxList[i][ini],
                                             tv=(self.allSkinJntsList[i], getWeights))

                    cmds.skinCluster(self.name + 'FacialGlobal_sct', e=True, ug=False, dr=4, ps=0, ns=10, lw=True, wt=0,
                                     ai=(self.dupallSkinJntsList))

                    if self.lidOtherGrp[0] == 'l':
                        cmds.copySkinWeights(ss=self.name + 'FacialGlobal_sct', ds=self.name + 'FacialGlobal_sct',
                                             mirrorMode='YZ',
                                             surfaceAssociation='closestPoint', influenceAssociation='closestJoint',
                                             mirrorInverse=False)
                    if self.lidOtherGrp[0] == 'r':
                        cmds.copySkinWeights(ss=self.name + 'FacialGlobal_sct', ds=self.name + 'FacialGlobal_sct',
                                             mirrorMode='YZ',
                                             surfaceAssociation='closestPoint', influenceAssociation='closestJoint',
                                             mirrorInverse=True)

                if self.lidOtherGrp[0] == 'l':
                    cmds.copySkinWeights(ss=self.name + 'FacialGlobal_sct', ds=self.name + 'FacialGlobal_sct',
                                         mirrorMode='YZ',
                                         surfaceAssociation='closestPoint', influenceAssociation='closestJoint',
                                         mirrorInverse=False)
                if self.lidOtherGrp[0] == 'r':
                    cmds.copySkinWeights(ss=self.name + 'FacialGlobal_sct', ds=self.name + 'FacialGlobal_sct',
                                         mirrorMode='YZ',
                                         surfaceAssociation='closestPoint', influenceAssociation='closestJoint',
                                         mirrorInverse=True)

    def setWeightCom(self, *args):
        if cmds.checkBoxGrp(self.mirrorChesk, q=True, v1=True) == False:
            self.allSkinWeightList = []
            print (self.name + 'FacialGlobal_sct')
            if self.name + 'FacialGlobal_sct' in cmds.ls():

                for i, rootVtxID in enumerate(self.allSkinVtxList):
                    skinWeightList = []
                    for vi, listVtxID in enumerate(rootVtxID):
                        cmds.skinPercent(self.facialGlobalSkin[0], self.polyObject + '.vtx[%s]' % listVtxID,
                                         tv=(self.facialGlobalJnt, 1))
                        getValue = cmds.gradientControlNoAttr(self.gredient, q=True, cvv=True,
                                                              vap=(self.SetNum * float(vi)))
                        skinWeightList.append(getValue)
                    self.allSkinWeightList.append(skinWeightList)
                cmds.select(cl=True)

                for i, weightIn in enumerate(self.allSkinWeightList):
                    for ini, getWeights in enumerate(weightIn):
                        if getWeights > 1:
                            getWeights = 1
                        cmds.skinPercent(self.facialGlobalSkin[0],
                                         self.polyObject + '.vtx[%s]' % self.allSkinVtxList[i][ini],
                                         tv=(self.allSkinJntsList[i], getWeights))
        if cmds.checkBoxGrp(self.mirrorChesk, q=True, v1=True) == True:
            self.allSkinWeightList = []
            if self.name + 'FacialGlobal_sct' in cmds.ls():
                for i, rootVtxID in enumerate(self.allSkinVtxList):
                    skinWeightList = []
                    for vi, listVtxID in enumerate(rootVtxID):
                        cmds.skinPercent(self.facialGlobalSkin[0], self.polyObject + '.vtx[%s]' % listVtxID,
                                         tv=(self.facialGlobalJnt, 1))
                        getValue = cmds.gradientControlNoAttr(self.gredient, q=True, cvv=True,
                                                              vap=(self.SetNum * float(vi)))
                        skinWeightList.append(getValue)
                    self.allSkinWeightList.append(skinWeightList)
                cmds.select(cl=True)

                for i, weightIn in enumerate(self.allSkinWeightList):
                    for ini, getWeights in enumerate(weightIn):
                        if getWeights > 1:
                            getWeights = 1
                        cmds.skinPercent(self.facialGlobalSkin[0],
                                         self.polyObject + '.vtx[%s]' % self.allSkinVtxList[i][ini],
                                         tv=(self.allSkinJntsList[i], getWeights))

                if self.lidOtherGrp[0] == 'l':
                    cmds.copySkinWeights(ss=self.name + 'FacialGlobal_sct', ds=self.name + 'FacialGlobal_sct',
                                         mirrorMode='YZ',
                                         surfaceAssociation='closestPoint', influenceAssociation='closestJoint',
                                         mirrorInverse=False)
                if self.lidOtherGrp[0] == 'r':
                    cmds.copySkinWeights(ss=self.name + 'FacialGlobal_sct', ds=self.name + 'FacialGlobal_sct',
                                         mirrorMode='YZ',
                                         surfaceAssociation='closestPoint', influenceAssociation='closestJoint',
                                         mirrorInverse=True)


if __name__ == '__main__':
    controls().baseWindow()
