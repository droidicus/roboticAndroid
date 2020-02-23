def main():
    with open('token', 'r') as f:
        token = f.readline()
        print('Token is: {}'.format(token))

if __name__ == "__main__":
    main()
    print('all done')
