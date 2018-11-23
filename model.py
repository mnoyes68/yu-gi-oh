class YugiohModel():
    def __init__():
        pass

    def residual_layer(self, input_block, filters, kernel_size):

        x = self.conv_layer(input_block, filters, kernel_size)

        x = Conv2D(
        filters = filters
        , kernel_size = kernel_size
        , data_format="channels_first"
        , padding = 'same'
        , use_bias=False
        , activation='linear'
        , kernel_regularizer = regularizers.l2(0.0001)
        )(x)

        x = BatchNormalization(axis=1)(x)

        x = add([input_block, x])

        x = LeakyReLU()(x)

        return (x)

    def conv_layer(self, x, filters, kernel_size):

        x = Conv2D(
        filters = filters
        , kernel_size = kernel_size
        , data_format="channels_first"
        , padding = 'same'
        , use_bias=False
        , activation='linear'
        , kernel_regularizer = regularizers.l2(0.0001)
        )(x)

        x = BatchNormalization(axis=1)(x)
        x = LeakyReLU()(x)

        return (x)

        def value_head(self, x):

        x = Conv2D(
        filters = 1
        , kernel_size = (1,1)
        , data_format="channels_first"
        , padding = 'same'
        , use_bias=False
        , activation='linear'
        , kernel_regularizer = regularizers.l2(0.0001)
        )(x)


        x = BatchNormalization(axis=1)(x)
        x = LeakyReLU()(x)

        x = Flatten()(x)

        x = Dense(
            20
            , use_bias=False
            , activation='linear'
            , kernel_regularizer=regularizers.l2(0.0001)
            )(x)

        x = LeakyReLU()(x)

        x = Dense(
            1
            , use_bias=False
            , activation='tanh'
            , kernel_regularizer=regularizers.l2(0.0001)
            , name = 'value_head'
            )(x)



        return (x)

    def policy_head(self, x):

        x = Conv2D(
        filters = 2
        , kernel_size = (1,1)
        , data_format="channels_first"
        , padding = 'same'
        , use_bias=False
        , activation='linear'
        , kernel_regularizer = regularizers.l2(0.0001) # Reg Constant
        )(x)

        x = BatchNormalization(axis=1)(x)
        x = LeakyReLU()(x)

        x = Flatten()(x)

        x = Dense(
            42
            , use_bias=False
            , activation='linear'
            , kernel_regularizer=regularizers.l2(0.0001) # Reg Constant
            , name = 'policy_head'
            )(x)

        return (x)

    def create_ygo_model(self):

        main_input = Input(shape = (2,) + (6,7), name = 'main_input')

        x = self.conv_layer(main_input, 75, (4,4))

        #if len(self.hidden_layers) > 1:
        for i in range(0,6):
            x = self.residual_layer(x, 75, (4,4))

        vh = self.value_head(x)
        ph = self.policy_head(x)

        model = Model(inputs=[main_input], outputs=[vh, ph])
        model.compile(loss={'value_head': 'mean_squared_error', 'policy_head': softmax_cross_entropy_with_logits},
            optimizer=SGD(lr=0.1, momentum = 0.9),   
            loss_weights={'value_head': 0.5, 'policy_head': 0.5}    
            )

        return model