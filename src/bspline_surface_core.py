def arquivostep(melhor, parordem, arquivosaida):
    ### BEGIN: allocating variables
    uknots = melhor[2]
    vknots = melhor[3]
    pesos = melhor[4]
    ptosctrl = melhor[5]

    # Defining the NURBS orders
    k = int(parordem[0])
    l = int(parordem[1])

    # Casting uknots from np.array to TColStd_Array1OfReal
    aux = np.unique(uknots)
    tam = np.size(aux)

    stepuknots = TColStd_Array1OfReal(0,tam-1)

    for i in range(0,tam):
        stepuknots.SetValue(i, aux[i])

    # Defining UMults
    stepumults = TColStd_Array1OfInteger(0,tam-1)

    stepumults.SetValue(0,k)
    stepumults.SetValue(tam-1,k)

    for i in range(1,tam-1):
        stepumults.SetValue(i,1)

    # Casting vknots from np.array to TColStd_Array1OfReal
    aux = np.unique(vknots)
    tam = np.size(aux)

    stepvknots = TColStd_Array1OfReal(0,tam-1)

    for i in range(0,tam):
        stepvknots.SetValue(i, aux[i])

    # Defining VMults
    stepvmults = TColStd_Array1OfInteger(0,tam-1)

    stepvmults.SetValue(0,l)
    stepvmults.SetValue(tam-1,l)

    for i in range(1,tam-1):
        stepvmults.SetValue(i,1)

    # np.shape(pesos) = np.shape(ptosctrl)
    [p,q] = np.shape(pesos)

    # Casting pesos from np.array to TColStd_Array2OfReal
    steppesos = TColStd_Array2OfReal(0,p-1,0,q-1)

    for j in range(0,q):
        for i in range(0,p):
            steppesos.SetValue(i, j, pesos[i][j])

    # Casting ptosctrl from np.array to TColgp_Array2OfPnt
    stepptosctrl = TColgp_Array2OfPnt(0,p-1,0,q-1)

    for j in range(0,q):
        for i in range(0,p):
            stepptosctrl.SetValue(i, j, gp_Pnt(ptosctrl[i][j][0], ptosctrl[i][j][1], ptosctrl[i][j][2]))

        ### END: allocating variables

    ### BEGIN: constructing NURBS surface
    stepnurbs = Geom_BSplineSurface(stepptosctrl, steppesos, stepuknots, stepvknots, stepumults, stepvmults, k-1, l-1, 0, 0)
    TopoDS_Face(BRepBuilderAPI_MakeFace(stepnurbs.GetHandle(), 1e-6).Shape())
    ### END: constructing NURBS surface

    ### BEGIN: writing STEP file
    stepcontroller = STEPControl_Controller()
    stepcontroller.Init()
    stepwriter = STEPControl_Writer()
    stepwriter.Transfer(steptopo, STEPControl_AsIs)
    stepwriter.Write(arquivosaida)
    ### END: writing STEP file