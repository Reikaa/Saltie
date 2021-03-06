from bot_code.modelHelpers import reward_manager


class EvalTrainer:
    file_number = 0

    display_step = 5
    current_file = None
    batch_size = 1000
    last_action = None
    reward_manager = None
    model_class = None
    eval_compare = {}

    def __init__(self):
        self.file_reward = 0
        self.file_frame_count = 0
        self.total_reward = 0
        self.frame_count = 0
        self.reward_manager = reward_manager.RewardManager()

    def get_model(self):
        # return rnn_atba.RNNAtba
        # return nnatba.NNAtba
        # return base_actor_critic.BaseActorCritic
        return self.model_class  # no need for a model if we're just calculating rewards

    def start_new_file(self):
        self.file_number += 1
        self.last_action = None
        self.reward_manager = reward_manager.RewardManager()
        self.current_file = None

    def process_pair(self, input_array, output_array, pair_number, file_version):
        if self.current_file is None:
            print(file_version)
            self.current_file = file_version
        rewards = self.reward_manager.get_reward(input_array)
        reward = rewards[0] + rewards[1]
        # print (input_array[8], reward, self.file_frame_count)
        self.total_reward += reward
        self.file_reward += reward

        self.frame_count += 1
        self.file_frame_count += 1

    def batch_process(self):
        # self.agent.update_model()
        # Display logs per step
        if self.file_frame_count % self.display_step == 0:
            print("File:", '%04d' % self.file_number, "Epoch:", '%04d' % (self.file_frame_count + 1))

    def end_file(self):
        self.batch_process()
        if self.file_frame_count == 0:
            return
        per_frame_award = self.file_reward / float(self.file_frame_count)
        if not self.current_file in self.eval_compare:
            self.eval_compare[self.current_file] = []
        self.eval_compare[self.current_file].append(per_frame_award)
        print('Reward for file:', self.file_reward)
        print('Reward per frame:', per_frame_award)

        self.file_reward = 0
        self.file_frame_count = 0
        self.reward_manager = reward_manager.RewardManager()
        # if self.file_number % 3 == 0:
        #     saver = tf.train.Saver()
        #     file_path = self.agent.get_model_path(self.agent.get_default_file_name() + str(self.file_number) + ".ckpt")
        #     saver.save(self.sess, file_path)

    def end_everything(self):
        print('\n\n\nREWARD RESULTS:\n\n\n')

        for key in self.eval_compare:
            list = self.eval_compare[key]
            average_reward_of_file = sum(list) / float(len(list))

            print('reward for bot [', key, '] is:', average_reward_of_file)
        # saver = tf.train.Saver()
        # file_path = self.agent.get_model_path(self.agent.get_default_file_name() + ".ckpt")
        # saver.save(self.sess, file_path)
