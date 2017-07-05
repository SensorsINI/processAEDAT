classdef QPBO  < handle

    properties
        qpboPtr=0
    end


    methods
        function qObj = QPBO()
            qObj.qpboPtr = qpbo_adapter('QPBO');

        end

        function  energy=getEnergy(obj)
            energy = qpbo_adapter('energy',obj.qpboPtr);

        end

        function  energy=labeltest(obj,labelings)
            energy=qpbo_adapter('test',obj.qpboPtr,labelings);

        end

        function  reset(obj)
            qpbo_adapter('reset',obj.qpboPtr);

        end

        function  merge_parallel_edges(obj)
            qpbo_adapter('merge',obj.qpboPtr);

        end

        function  labels=probe(obj)
            labels=qpbo_adapter('probe',obj.qpboPtr);
        end

        function  obj=add_node(obj)
            qpbo_adapter('add_node',obj.qpboPtr);
        end
        function  obj=add_multiple_nodes(obj,num)
            qpbo_adapter('add_multiple_nodes',obj.qpboPtr,num);
        end

        function add_unary_term(obj,xi,e0,e1)
            qpbo_adapter('add_unary_term',obj.qpboPtr,xi,e0,e1);
        end

        function  add_pairwise_term(obj,xi,xj,e00,e01,e10,e11)
            qpbo_adapter('add_pairwise_term',obj.qpboPtr,xi,xj,e00,e01,e10,e11);
        end

        function  solve(obj)

            qpbo_adapter('solve',obj.qpboPtr);

        end

        function label=get_label(obj,node_id)%TODO set default segment
            label = qpbo_adapter('get_label',obj.qpboPtr,node_id);
        end
        %
        function labels = all_labels(obj)
            labels = qpbo_adapter('all_labels',obj.qpboPtr);
        end
        %
        function segments = all_segments(obj)
            segments = qpbo_adapter('all_segments',obj.qpboPtr);
        end

        function create_from_theta(obj,theta_p,theta_pq)
            qpbo_adapter('create_from_theta',obj.qpboPtr,theta_p,theta_pq);
        end

        function nodenum=create_from_theta_pqr(obj,theta_pqr)
            nodenum=qpbo_adapter('triple',obj.qpboPtr,theta_pqr);
        end

        function energy=set_labels(obj,imgVector)
            energy=qpbo_adapter('set_labels',obj.qpboPtr,imgVector);
        end
        function compute_weak_persistencies(obj)
            qpbo_adapter('compute_weak_persistencies',obj.qpboPtr');
        end
        function improve(obj)
            qpbo_adapter('improve',obj.qpboPtr);
        end
        function save(obj)
            qpbo_adapter('save',obj.qpboPtr);
        end
        function create_from_monoms3(obj,unary,pairwise,m,n)
            qpbo_adapter('fromMonoms3',obj.qpboPtr,unary,pairwise,m,n);
        end

        function destroy(obj)
            qpbo_adapter('destroy',obj.qpboPtr);
        end

    end






end
